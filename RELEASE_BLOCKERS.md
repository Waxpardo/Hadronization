# Release blockers — the finite remaining scope

**Produced:** 2026-08-04, session v5, at `e690e17`.
**Rule:** this list is closed. Anything not on it that is worth doing goes to
`POST_SUBMISSION.md`. Anything a paper claim depends on that is not yet verified
goes here.

Every row cites `path:line` or a SHA. Where I ran something and can quote the
output line, it says so. Where I have not, it says *not run*.

---

## 0. The claim-to-evidence inventory it derives from

**The paper is 589 lines across 7 `.tex` files and is largely a skeleton.**
`Results.tex:159` is literally `\textbf{UNDER CONSTRUCTION -- placeholder text
from thesis}`; `Summary.tex` is one truncated sentence. So the inventory is
short, and concentrated in `Model.tex`.

**Read this first, because it inverts the expected finding.** The three
superseded figures the brief asked me to hunt — the ~3.2x baryon ratio, the
0.44 % differential systematic, and −4.2 % stated generally — **are not in the
paper at all.** `grep` over all seven `.tex` files returns zero hits for `3.2`,
`3.68`, `0.44`, `0.59`. They exist only in `docs/handoffs/` (v3:412-414,
v4:558,770,797). They are internal working numbers that were never promoted into
the manuscript. There is nothing to flag and nothing to correct.

The real exposure is the opposite shape: the paper states numbers from a
**superseded production and a superseded PYTHIA version**, and its headline
results section makes almost no quantitative claims at all.

| # | Claim (quoted, `.tex` line) | Evidence chain — what must hold | Verifying artifact | Status |
|---|---|---|---|---|
| C1 | `Model.tex:39` "`PhaseSpace:pTHatMin = 1.`" | The paper's stated threshold equals the one production used | All three cards set `PhaseSpace:pTHatMin = 2.` (`SimulationScripts/pythiasettings_Hard_Low_ccbb_{MONASH,JUNCTIONS,CLOSEPACKING}.cmnd`); decision recorded `ValidationReports/PTHAT_MULTIPLICITY_SCAN_8317.md:117` | **CONTRADICTED** — paper says 1.0, production is 2.0 |
| C2 | `Model.tex:40-42` "Events per job $10^{6}$ / Jobs per tune $100$ / Events per tune $10^{8}$" | The stated campaign shape equals the configured one | `Makefile:25-26` sets `JOBS ?= 1000`, `EVENTS ?= 100000`. Same 10^8 total, **different shape** | **CONTRADICTED** — this is the fossil 100 x 1,000,000 shape |
| C3 | `Model.tex:126` "mean charged-particle density about $36\%$ below minimum bias ... threshold $p_T^{hat} > 1$ GeV" | The deficit figure is measured on the production generator at the production threshold | Measured this session, cluster 5319322: −28.6 % at pTHatMin 1.0, **−4.16 % at 2.0** on 8.317. `PTHAT_MULTIPLICITY_SCAN_8317.md:78` says explicitly "The paper's current number is wrong" | **CONTRADICTED twice** — wrong PYTHIA version (36 % is 8.315) *and* wrong threshold |
| C4 | `Model.tex:55` "it yields $dN_{ch}/d\eta = 7.01$ ... compared with $6.94\pm0.10$" | The MB calibration number is the current one | Measured this session: **6.968** (`a2_multiplicity/logs/MB.out`, `A2_EXIT=0`) | **STALE** — 7.01 is 8.315-era; 6.968 is the 8.317 value. Conclusion (counter is sound) survives |
| C5 | `Model.tex:60` "MONASH and JUNCTIONS differ in 13 effective settings, and MONASH and CLOSEPACKING in approximately 20" | The counts match the audited card diff | `Validation/AuditTuneSettings.C`, surfaced by `make check` as `TUNE_CARD_DIFFERENCE` lines | **VERIFIABLE — NOT RUN.** The count was not tallied this session |
| C6 | `Model.tex:82` table of generated yields | Yields come from the final campaign | Self-flagged in the paper: "**[TO BE REGENERATED: the numbers currently in this table come from a superseded production]**" | **NO ARTIFACT YET** — awaits full production |
| C7 | `Model.tex:55` "Disabling heavy-flavour decays biases this by $1.3\%$" | The bias is measured, not asserted | No artifact located. The A2 macro has a `disableHeavyDecays` switch that could measure it, but no recorded run does | **NO ARTIFACT EXISTS** |
| C8 | `Model.tex:126` percentile classes "not equivalent to experimental minimum-bias multiplicity classes" | The offset is known **per tune**, since percentiles are computed within each tune's own sample | MONASH measured (−4.16 % at 2.0). JUNCTIONS and CLOSEPACKING **unmeasured** | **PARTIAL** — see B4, the central one |
| C9 | `Results.tex:162-166` prose on Sigma_b / Lambda_b enhancement, `ProbQQ1toQQ0join` | The described enhancement is present in this pipeline's merged output | Prose is thesis-era, describes MONASH vs JUNCTIONS only; **CLOSEPACKING absent from the narrative** though present in every figure | **NO ARTIFACT** — narrative not tied to any run of this pipeline |
| C10 | `Results.tex` figures 2-8, `figures/...PDF_215.pdf` etc. | Figures were produced by the live chain from merged output | `_215` naming indicates thesis-era product. Not traced to any `run_paper_plots.sh` target | **NO ARTIFACT** — provenance unestablished |

**Claims with no artifact at all — what a referee finds: C7, C9, C10, and C6
until production lands.**

---

## THE PRODUCTION-GATE LIST — G1, and it is a closed set

**Recorded 2026-08-09. This is the whole list of things that gate
`make submit-full ORDINAL=3`. Nothing else does.**

**G1 — REMAINING CONTENT AS OF 2026-08-09 is exactly two things:**

1. **The Nikhef sync** (freeze ends there).
2. **The submit-readiness walk**, ending in a READY/NOT-READY statement.

**When those two are done and the owner says GO, `submit-full ORDINAL=3`
follows.**

**Already discharged off G1:**

| was on G1 | disposition |
|---|---|
| **F1** — variation weights | **SIGNED OFF** 2026-08-09, §F1 below |
| **B2** — `submit-full` seed burning | **LANDED** `81a350c`, all three targets burn |
| **B9** — retry ordinal | **CLOSED**, already fixed by `e403853` |
| **B13** — closure log on failure | **LANDED** `f44b3c1` |
| **B6** — rung-6 targets at 300-job scale | **CLOSED** 2026-08-09 by owner ruling — see §B6 below |
| **guard demotion** | **STRUCK from G1** under the shrink rule — see below |

#### The "guard demotion" — antecedent identified and struck, 2026-08-09

**This resolves a reference that dangled through five handoffs.** Every prior
mention (`HANDOFF_v7:281`, `v8:340`, `v9:155`, `v10:131`, and this file) said
only "the guard demotion" with no antecedent.

**It is the per-tune CPU guard.** Identified by exact phrase match:
`POST_SUBMISSION.md:236` reads *"Implement after the post-merge sync, alongside
B2 and B9"* — the same pairing every deferred list used — under the heading
*"Per-tune CPU guard — moved here from RELEASE_BLOCKERS.md, 2026-08-05"*.

- **Which guard:** `MAX_CPU`, the hang guard.
- **Demoted from what to what:** from a **release blocker** to **production
  hygiene**, on **2026-08-05**, by owner decision on the measured tail — the flat
  3600 s guard is not killing healthy jobs (`POST_SUBMISSION.md:234-235`).
- **Struck from G1:** 2026-08-09, by the owner, under the shrink-only rule.
- **Verified margins:** the proposed per-tune guard at 5x median gives headroom
  **2.2x / 2.4x / 2.8x** over estimated max at n=1000 (MONASH / JUNCTIONS /
  CLOSEPACKING) — **all >2x**, so the flat guard is the conservative choice and
  nothing is at risk by deferring.

**It remains post-production hygiene in `POST_SUBMISSION.md`. The dangling
references are now resolvable from here.**

**THE SHRINK-ONLY RULE, verbatim:**

> **The list only shrinks. Any proposed addition is a STOP naming the cost of
> delay.**

**What is deliberately NOT on it, and why.** With the production shape closed
(G2, below) and stage-1 of the registry work being analysis-side only, **nothing
that remains open affects what the generator writes** except F1.

| open work | gates | does NOT gate |
|---|---|---|
| **B4 / axis decision** | **figures** | generation, submission |
| **stage-1 registry work** | **analysis** | generation, submission |
| **stage-2 registry work** | a *future* campaign | this one |

**Both proceed in parallel with generation.** A post-generation gate on figures
is not a pre-generation gate on the run that produces them.

### G2 — PRODUCTION SHAPE: CLOSED. Option A, combined production

**Decided 2026-08-09 on measured evidence.** Full record in
`docs/PRODUCTION_SHAPE_DECISION.md`; measurement commit `5ed3bc9`.

**Basis:** every quoted beauty species clears **≥10 mean entries per block in
every class, in all three tunes**, projected to 1000 jobs from exact per-block
`hCorrelations` integrals. **Binding value: MONASH Σ_b^± class 1 = 20.**

**B_c is declared a multiplicity-integrated / top-class-only observable** in the
paper's scope. It fails per-class viability under every scheme tested (c1–c7 at
11 classes; coarse classes 1–2 at 4 classes), and that is a property of combined
production, not a defect. **The bb̄-only top-up survives as a post-submission
option in its cheapest shape** — see `POST_SUBMISSION.md`.

**Σ_b⁰ stays measured-not-quoted** (`centralEligible = false`). **Any
completeness table that includes it inherits its class-1 failure (7 entries) and
must say so.**

**Corrected statistics facts, recorded so the superseded ones cannot return:**

- **Event ratio cc̄:bb̄ = 6.39:1** (beauty fraction 13.5 %), tune-independent,
  measured over 10⁶ events/tune from `process_counts`.
- **The superseded "~10:1" came from the C6 table's *accepted-quark* counts read
  as an *event* ratio** — a measurement-scope error of the catalogued class, on
  the design side. **A quark-level ratio is a different quantity and must be
  labelled as one.**
- Split gain: **≤7.39x per event (BOUND** = 1/0.1354); **~4x per CPU-hour
  (ESTIMATE**, assumes per-event CPU scales like N_ch — unmeasured).

### M6. The pooled percentile axis is not a common axis — PRODUCTION-BLOCKING for figures

**Measured 2026-08-08, 10⁶ events per tune.** The charm-hard and beauty-hard
populations are **exclusive by construction** — `hard_channel==4` ↔ process codes
121/122, `==5` ↔ 123/124, **zero cross-contamination in either direction, all
three tunes.**

| | measured |
|---|---|
| pooled sample composition | **86.5 % charm-hard** |
| N_ch means, charm vs beauty | **9.675 / 20.172** (MONASH), 10.685 / 21.725, 10.053 / 20.289 — **ratio 2.02–2.09x** |
| beauty occupancy, class 1 → class 11 | **3.0 % → 45.3 %**, a **13–15x swing** |

**So a pooled percentile class is a variable-composition mixture, and the
composition is what changes along the axis.** It cannot carry a charm-vs-beauty
comparison at fixed class.

**REMEDY DECIDED 2026-08-09 — common absolute N_ch boundaries. M6 CLOSES by
construction.**

> **One boundary set, shared by all three tunes AND both sectors. Labels are
> percentiles of the MONASH MB distribution. The per-tune MB-percentile
> translations are published as a table.**
>
> **Boundaries (half-integer, so no integer N_ch is ambiguous):**
> `−0.5, 2.5, 3.5, 5.5, 6.5, 8.5, 10.5, 13.5, 17.5, 23.5, 32.5`
>
> **Maximum published residual: 2.91 pp.** Full boundary and translation tables
> in `docs/PRODUCTION_SHAPE_DECISION.md` §5c.

**Why this closes M6 rather than mitigating it.** M6's defect was that a pooled
per-tune percentile class is a *variable-composition mixture* — the class
definition itself moved with the sample. **A common absolute boundary is the
same event selection for every tune and both sectors**, so the 13–15 % → 45 %
occupancy swing is no longer hidden inside the class definition; it becomes a
property of the data that the published translation makes visible.

**Rejected: MB-anchored PER-TUNE boundaries**, which was the working preference
until this session. **Rejected on physics, not on the failed gate.** Per-tune
percentile classes fold each tune's activity distribution into the class
definition, confounding *hadronisation at fixed activity* with *activity
distribution* — the two things this study exists to separate. **Had B4's ±3 pp
gate passed, per-tune anchoring would still have been wrong for this reason.**

**The B4 escalation that surfaced it is accepted as a RESULT, not an artifact:**
5 of 11 boundaries outside ±3 pp, failures concentrated where the MB density
peaks, JUNCTIONS the outlier on both arms, ordering coherent with `pT0Ref`
(2.15 → most MPI → highest MB mean; MONASH 2.28 and CLOSEPACKING 2.194 nearly
degenerate at 0.8σ). **The measuring session's 0.8σ qualification on the
difference check is accepted as an owner judgement** — hard arms at 12.6σ and
provably distinct cards settle plumbing, and the MB near-degeneracy is itself
physics.

**One consequence checked, not assumed:** new boundaries move the class windows,
so **6(iii)'s Option-A verdict is re-evaluated under them** — see the memo.

**Non-gating follow-up:** a boundary-grade MB reference run per tune for
0–1 % tail precision, with a settings echo added to the macro first. **Gates
figures, not the farm.**

**FRAMING CAVEAT, and it must travel with the remedy.** MB-anchoring is adopted
as **the standard experimental convention, with quantified residuals** (B4's
mapping) and **per-class ⟨N_ch⟩ quoted per tune**. **It does not claim the
cross-tune axis question dissolves** — it makes the residual explicit and
bounded instead of implicit and unbounded. Anyone reading "MB-anchored" as "the
problem is solved" has over-read it.

**This gates figures, not generation.** The activity axis is a full-resolution
stored quantity; class boundaries are a downstream choice.

### The excited-state gate — points at the STAGED proposal

`docs/REGISTRY_AND_MAPPING_PROPOSAL.md`, restaged 2026-08-09.

**Stage-1 is analysis-side only and does NOT gate generation** — no card,
producer or registry change; pair count stays 300. **Stage-2 is deferred and
rides a future campaign generation in full.**

**✅ RULED 2026-08-20 — stage-1 is DEFERRED past this paper, and the two design
gaps go with it.**

The two gaps stay unresolved and stated: the **§0a/§4B eligibility conflict**
(dissolved in stage-1 by construction, live again in stage-2) and the
**`ValidateRawInputs` contract transition**.

**The reason is that the argument for acting has inverted, and the inversion is
measured rather than judged.** The proposal's case for implementing stage-1 was
a cost window:

> **This is the standing argument for implementing before full production.**
> Doing it after means regenerating the full campaign (562.5 CPU-h) instead of
> the 10 % one, a **10x** difference — or living with versioned acceptance
> permanently.

**That window is closed.** `HF_RUN3_V1` is generated, merged, sealed and
promoted to `canonical` with `publication_eligible: true`
(`docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md`). The cheap side of the 10×
comparison no longer exists. Any registry change now faces the **562.5 CPU-h**
figure or permanent versioned acceptance, which is the outcome the proposal
named as the thing to avoid.

**And nothing waits on it.** No figure, table or blocker in this release depends
on excited-state recording. `ValidateRawInputs` pins the current registry to
compiled constants, so leaving the registry alone is also what keeps every
existing raw file acceptable.

**Recorded as deferred, not dropped.** The proposal stays staged and its two
gaps stay written down, so a future campaign inherits the analysis rather than
re-deriving it. **What must not happen is that stage-1 is implemented against
the sealed campaign** — that would reject every raw file the paper's numbers
come from.

### B15b. Seed derivation ignored the campaign — CLOSED 2026-08-09, `12b1f1a`

**The one authorized addition to the gate list.** Added by the owner; cost of
delay one session with the farm idle; closed the same session on green evidence.

**The finding.** `seed_for()` derived seeds from `(tune, job_index, attempt)`
only — **no campaign term.** Every campaign at attempt 0 drew the same sequence
from `SEED_BASE = 100000001`. `make submit-full ORDINAL=3 CAMPAIGN=HF_RUN3_V1`
tried to draw seeds the ledger labels `# HF_SMOKE attempt0`. **B2's
`assert_seeds_unused` caught it at render: nothing burned, no `.sub` written,
ledger unchanged at 430/430.** It is the first production-scale test of that
guard, and the guard is the reason this is a near-miss rather than an incident.

**Retrodiction check, done before any code changed.** Only two `seed_for`
callers, both forward-looking. `campaign_status.py:73,95` **reads** `seed` from
stored payloads rather than re-deriving it, so historical campaigns validate
against their own recorded metadata. **No derivation versioning needed.**

**Ratified design — `seed_derivation_v2`:**

```
seed = SEED_BASE + ordinal*CAMPAIGN_STRIDE + tune*TUNE_STRIDE
     + attempt*ATTEMPT_STRIDE + job_index      CAMPAIGN_STRIDE = 10_000_000
```

`campaign_ordinal` is **keyword-only with no default** — a default is precisely
how v1's bug would return. `MAX_CAMPAIGN_ORDINAL` is **derived (= 79)**, not
hardcoded, and out-of-range ordinals **raise rather than truncate**.

**THE HISTORICAL AUDIT — and it overturned its own expectation.**
**Zero realised collisions in 430 entries.** The reason is the finding:
**the attempt axis had already been used as a campaign counter.**

| campaign | attempts consumed |
|---|---|
| HF_SMOKE | 0 |
| HF_SMOKE2 | 1, 2, 3 |
| HF_PT2 | 4, 5 |
| HF_PT2_INT | 6, 7 |

**Attempts 0–7 of `MAX_ATTEMPTS = 10` were gone; only 8 and 9 remained.**
The pre-registered expectation — that HF_SMOKE-era seeds collide with later
attempt-0 campaigns — was **wrong**: there were no later attempt-0 campaigns,
because each campaign silently advanced the attempt instead. **HF_PT2_INT is
internally collision-free** (300 + 8 entries, all unique) — that half held.

**Disposition: documented, never repaired.** No ledger edit, no data action.
The overlap never materialised, smoke data never enters an analysis, and event
IDs carry the campaign ordinal independently. **v2 prevents recurrence and
returns the attempt axis to retry-only use** — HF_RUN3_V1 runs at attempt 0
with all ten attempts available.

**Rejected alternatives, recorded so they are not retried:**

- **Advance `SUBMIT_ATTEMPT`.** Refused, and the audit strengthens the refusal
  from semantic to arithmetic: **only attempts 8 and 9 remained**, so a 3000-job
  campaign needing two-to-three retry rounds at ~2.7 % would have **run out of
  attempt slots mid-production.**
- **A per-campaign `SEED_BASE` offset.** No schema change, but the offset lives
  nowhere durable and becomes the next lost antecedent.

**Closure evidence:** `12b1f1a`; `tests/test_seed_derivation.py` pins the
property (cross-campaign disjointness, the specific v1 collision, cap failing
closed both ends, mandatory ordinal); suite **24 → 25, pre-registered, 25/25
green**.

### F1. Variation weights — SIGNED OFF, 2026-08-09. G1 gate CLOSED

**Decision: PYTHIA automated variation weights stay OFF for full production.**
Owner-signed 2026-08-09. Full rationale in `docs/DESIGN_AND_RATIONALE.md` §3.15.

**Leg (a) — VERIFIED.** `event_weight` is a scalar `double`
(`heavyflavourcorrelations_status.cpp:709`); `sum_weights`/`sum_weights2` are
scalar doubles (`:849-850`, `:1402-1403`, `:1622-1623`), read through
`ReadScalar` at `Validation/ValidateRawOutput.C:466-467`. **`:976` pins the
schema explicitly as `{"event_weight", "Double_t", 1}` — a declared contract
asserting exactly one double per event**, not merely code that assumes scalars.
**18 files touch the weight contract.** Cost of ON: raw **88.0 MiB/job** (27 GB
at 300 jobs → ~264 GB at 3000) growing **~+18 %** at N≈20 weights → ~312 GB;
CPU overhead **10–30 %, ESTIMATE, not measured**.

**Leg (b) — repo-side verified, PYTHIA-API-side argued, and the distinction is
kept.** *Verified:* no hadronisation-variation weighting exists anywhere in the
tree. *Argued, not tested:* PYTHIA's automated machinery reweights parton-shower
emissions and PDF members, while hadronisation parameters act after the shower
and change which hadrons form, so there is no fixed configuration to reweight.

**The decisive line:** **the three arms are themselves the hadronisation
variations, handled by separate runs.** Weights would buy only shower/PDF
systematics — which are **argued in the referee response, not computed**. That
ties directly to **B14**, where nothing is computed today either, and the two
were signed together.

**No longer on G1.**

### CLOSED 2026-08-20 — the review document is UNAVAILABLE, and the citations are gone

**Owner ruling: no such document exists.** The physics review that earlier
entries cited as `M1`–`M10` was never written down in a form that can be filed.
A search of the Projects tree on 2026-08-20 found none, which agrees with the
owner.

**So the citations were removed rather than left pointing at nothing.** Three
lines in this file and one in `docs/REGISTRY_AND_MAPPING_PROPOSAL.md` cited the
review **as a document**. Each now states the finding it was carrying, so a cold
reader gets the substance instead of a reference they cannot follow.

> **The findings survive the source's absence.** B15 lists four that this
> repository recorded independently — B1, B5, B8 and the Σ_b naming requirement
> — and each is measured and cited in-tree. Losing the review loses the
> provenance of the prompting, not the evidence.

> ### ⚠ THE `M` PREFIX MEANS THREE DIFFERENT THINGS — a finding for the documentation pass
>
> This sweep had to be done by hand, and the reason is a naming collision that
> is still live:
>
> | token | meaning | example |
> |---|---|---|
> | `M1`–`M5` | **the A2 multiplicity classes** | `STATE.md` PENDING 8, "JUNCTIONS 0.0255 (M1) … 0.1509 (M4)" |
> | `M7` | **the unresolved-origin measurement and its macro** | `docs/M7_UNRESOLVED_SYSTEMATIC.md` |
> | `M1`–`M10` | **the physics review's findings** | the three lines this entry replaces |
>
> **`M2` alone carries two of the three.** It is an A2 class *and* a review
> finding with its own document, `docs/M2_PROBQQ1TOQQ0JOIN.md`.
>
> **A mechanical sweep of `M<digit>` would have corrupted working documents**, so
> only the four lines that cite the review *as a document* were rewritten.
> `POST_SUBMISSION.md:426` mentions "M2's open half" and was **deliberately left
> alone**: it resolves to `docs/M2_PROBQQ1TOQQ0JOIN.md`, which a reader can open,
> so it is not a dangling citation.
>
> **Recommendation for the documentation pass:** if the review ever arrives, file
> its findings under a **distinct prefix** — `R1`–`R10` or similar — rather than
> reusing `M`. One prefix with three meanings is a trap for exactly the kind of
> sweep this entry describes.

---

## Blockers

### B1. The methods section describes a different study from the one being run

**Owner action. The paper is not to be edited by an agent; the owner has said
they will make these changes themselves.** Exact locations and replacement
values, all four in `Model.tex`:

| Line | Currently reads | Should read | Evidence |
|---|---|---|---|
| **`:39`** | `PhaseSpace:pTHatMin = 1.` | **`PhaseSpace:pTHatMin = 2.`** | All three cards set `= 2.`: `SimulationScripts/pythiasettings_Hard_Low_ccbb_{MONASH,JUNCTIONS,CLOSEPACKING}.cmnd`. Decision recorded `PTHAT_MULTIPLICITY_SCAN_8317.md:117` |
| **`:40`** | Events per job $10^{6}$ | **$10^{5}$** | `Makefile:26` `EVENTS ?= 100000` |
| **`:41`** | Jobs per tune $100$ | **$1000$** | `Makefile:25` `JOBS ?= 1000` |
| `:42` | Events per tune $10^{8}$ | **unchanged** | 1000 x 10^5 = 10^8. Only the factorisation is wrong, not the total |
| **`:55`** | `dN_ch/d\eta = 7.01` | **`6.968`** | Measured this session, `a2_multiplicity/logs/MB.out`, `A2_EXIT=0`. Note this *strengthens* the sentence: 6.968 is closer to the quoted 6.94 ± 0.10 than 7.01 was |
| **`:126`** | "about $36\%$ below minimum bias ... threshold $p_T^{hat} > 1$ GeV" | **"about $4\%$"** (measured −4.16 %) **and $> 2$ GeV** | Measured this session, cluster 5319322: 6.678 vs MB 6.968. `PTHAT_MULTIPLICITY_SCAN_8317.md:78` states outright "The paper's current number is wrong" |

**`:126` is the one that matters, and a number swap is not sufficient.** The
sentence does not merely quote 36 % — it *reasons from* it, concluding that the
classes "are therefore not equivalent to experimental minimum-bias multiplicity
classes" and that comparisons "should be read as qualitative trends rather than
as matched event classes". At −4.16 % that reasoning no longer follows. The
conclusion may still be right for other reasons — **which is exactly what B4
now measures** — but it cannot rest on this number any more. Whoever rewrites
`:126` should wait for B4 rather than simply substituting 4 % for 36 %.

Two of these are the same fossil the Phase 4 checklist tracks: `:40-41` is the
100 x 1,000,000 shape.

### B2. `submit-full` does not record its seeds
`--burn-seeds` is passed in exactly two places: `Makefile:155` (`submit-smoke`)
and `tools/resubmit_held.py:186`. **`submit-full` and `submit-prelim` render
without burning.** Full production would queue 3000 jobs and record none of
their seeds, after which a later campaign at the same attempt would collide
silently — `assert_seeds_unused` passes because nothing was written.
Worked around this session by invoking the renderer directly with
`--burn-seeds` (ledger 122 -> 422, verified no duplicates). That was right for
one campaign and **is not a plan for 3000 jobs.**

**Do this before anything else touches production.** Two parts:

1. `submit-full` must pass `--burn-seeds`.
2. **Decide `submit-prelim` explicitly and comment the decision in the
   Makefile.** Right now the asymmetry — smoke burns, prelim does not, full does
   not — reads as an accident rather than a choice, and there is no comment
   anywhere saying which it is. Either prelim burns like the others, or the
   reason it must not is written down next to it. An undocumented asymmetry in
   the one mechanism protecting an irreplaceable global resource is the shape of
   defect this project has already been bitten by twice (v4 section 10,
   pattern 2).

Worth noting for whoever fixes it: `burn_seeds`' own docstring says *"Call once
a job has actually been submitted"* (`campaign.py:135`), but every caller burns
at **render** time, before `condor_submit`. That is already inconsistent with
the stated contract and should be resolved in the same pass rather than
deepened.

### B3. `kinematic-spectra` is blocked; the kinematic gate has no producer
Handoff v4 section 6a. `freeze_summary.json` and
`canonical_raw_validation_receipt.json` have no writer since `1ed6114`, and
`freeze_seal.json` omits the three keys the gate asserts
(`state`, `validation_receipt_path`, `validation_receipt_sha256`).
The owner's derivability list is in v4 section 6a and the binding constraint is
recorded there: derive from evidence or remove the assertion with a rationale;
never synthesise a literal.

### B4. The multiplicity percentile classes are not shown to be a common axis
**This is the one that undermines the central comparison, and it is now
half-answered.** Percentiles are computed within each tune's own sample. This
session measured MONASH's offset (−4.16 % at pTHatMin 2.0) and reproduced all
five scan points bit-exactly. JUNCTIONS and CLOSEPACKING remain **unmeasured**.

The cards make the concern concrete rather than theoretical:
`MultipartonInteractions:pT0Ref` is **2.28** for MONASH (PYTHIA default via
`Tune:pp = 14`), **2.15** for JUNCTIONS, **2.194** for CLOSEPACKING. The
production threshold 2.0 sits below all three, but by very different margins
(0.28 / 0.15 / 0.194). If the offsets differ materially, "0-20 %" is not the
same physical region across arms and the three-tune comparison is sliced on an
axis that is not common.

**Decided this session, not yet implemented:** extend
`Validation/CalibrateMultiplicityAgainstMinBias.C` to read the production card
and re-apply the A2 convention afterwards; use a per-tune minimum-bias
reference *and* quote the common ALICE value. 15 jobs (3 tunes x 5 points).

#### The measurement that actually answers this — added after owner review

**The offset from MB is the intermediate quantity, not the answer.** Percentile
classes are self-normalising within each tune, which is standard and fine. The
real question is *what "0-20 % of our hard sample" corresponds to in that tune's
own minimum-bias distribution.*

**Deliverable: for each tune, the mapping from hard-sample percentile boundary
to MB percentile.** Concretely — take each hard-sample percentile boundary in
`N_ch`, then ask what percentile that same `N_ch` value sits at in *that tune's*
minimum-bias distribution.

- If MONASH's hard 0-20 % maps to MB 0-18 % and JUNCTIONS' maps to MB 0-25 %,
  the three arms are compared at **different event activities while appearing to
  be at the same selection**.
- If the three mappings agree to within a few percent, the comparison is clean
  and the paper has the one sentence that answers the referee on this point.
- If they diverge, that is a real result about the analysis design, and it is
  needed **before** production, not after.

**This requires the full `N_ch` distribution per tune for both arms, not just
the mean** — the current macro reports only means (`<N_ch>` and
`dN_ch/d\eta`). Extending it must therefore also retain the per-event `N_ch`
distribution so percentiles can be computed on both sides. That is a larger
change than the tune-plumbing decided above, and it is the substantive part.

**Report only. Propose no change to the threshold without asking.**

### B5. Tune-difference counts in the paper are unverified — MEASURED, both wrong

**Closed by measurement 2026-08-05.** `Validation/AuditTuneSettings.C` run over
HF_PT2_INT `job000` of each tune: `EFFECTIVE_TUNE_AUDIT errors=0 settings=1998
differences=21`, tallied pairwise from its CSV.

| Contrast | Measured | Excluding `Random:seed` | Paper says |
|---|---|---|---|
| MONASH ↔ JUNCTIONS | 10 | **9** | **13** |
| MONASH ↔ CLOSEPACKING | 16 | **15** | **~20** |
| JUNCTIONS ↔ CLOSEPACKING | 18 | **17** | — |

`Random:seed` differs only because these are different jobs; it is not a tune
setting and must be excluded. **Both stated counts are too high** — 13 → 9 and
~20 → 15. A one-word fix in `Model.tex:60`, owner action per B1.

**And the parenthetical on that line is wrong for the tune it names.**
`Model.tex:60` says MONASH and CLOSEPACKING differ "**including the Lund
fragmentation parameters $a$ and $b$** and the multiparton-interaction
regularisation scale". Measured, `StringZ:aLund` and `StringZ:bLund` **do not
differ between MONASH and CLOSEPACKING at all** — they differ between MONASH and
*JUNCTIONS*. `MultipartonInteractions:pT0Ref` does differ, so half the
parenthetical holds and half does not.

**This confirms the CLOSEPACKING control independently, and more strongly than
the card diff did.** The full MONASH ↔ CLOSEPACKING difference list is:

```
BeamRemnants:remnantMode                    ColourReconnection:mode
ClosePacking:baryonSup                      ColourReconnection:m0
ClosePacking:doClosePacking                 ColourReconnection:mPseudo
ClosePacking:doEnhanceDiquark               ColourReconnection:junctionCorrection
ClosePacking:enhancePT                      ColourReconnection:allowDoubleJunRem
ClosePacking:enhanceStrange                 MultipartonInteractions:pT0Ref
StringFragmentation:doStrangeJunctions      StringZ:useOldAExtra
StringFragmentation:enhanceStrangeJunction
```

**`StringFlav:probQQ1toQQ0join`, `probQQtoQ`, `probStoUD`, `StringZ:aLund` and
`bLund` are all absent** — CLOSEPACKING holds *every* flavour-composition and
Lund fragmentation parameter at its Monash value, while differing from MONASH in
CR, close packing, strange junctions and `pT0Ref`. That is a materially better
controlled contrast than the card diff suggested, and it is why the "CR drives
Sigma_b, the diquark parameter does not" argument holds: the parameter is
*identical* across the pair that shows the effect, not merely similar.

Note this is exactly why a card diff could not settle it — CLOSEPACKING states
`probQQ1toQQ0join = 0.5,0.7,0.9,1.0` explicitly while MONASH inherits the same
values from `Tune:pp = 14`, so the line differs and the *effective setting* does
not.

### B6. Two rung-6 targets are unexercisable below full scale — **CLOSED 2026-08-09**

`thnsparse` and `audit-subsamples` (v4 section 4). **Both now execute end to end**
over HF_PT2_INT, the 10M-event intermediate campaign. **v4 precondition 12 is
discharged**: they are no longer first exercised for real by full production.
`docs/B6_STATUS.md` is the full record.

**What unblocked it.** For six generations neither target could run at all — no
`hf_pt2_int` dataset existed in either selector, so there was nothing to resolve.
The entry was added (the one authorized config edit, `76445b6`) and validates on
Nikhef: `DATASET_SELECTOR_VALID active=hf_pt2_int_candidate
status=canonical_candidate blocks=10`.

**The scoping mechanism.** There was **no per-observable bin scoping in the
plotting configuration at all** — `subsample_error_bins_to_exclude` matches on
bin name alone, and the audit deliberately zeroes it — so G2's B_c scope could
not be encoded config-only. An optional **per-pair `multiplicity_scope`** was
added; empty means all bins, and it is honoured **even under the audit**.

| | before scoping | after |
|---|---|---|
| total failures | **54** | **6** |
| `BplusBcminus.root` | 14 | **0 — gone** |
| `LbbarBcminus.root` | 40 | **6** |
| bins affected | all classes | **only `M0_1`** |
| charm | 0 | 0 |

**48 of 54 cleared, and exactly the out-of-scope ones.**

**The residual six, and why they close as a statistics limitation.** All six are
**Λ̄_b × B_c⁻ in `M0_1`**, and all six report `yield zero in all blocks
(coverage complete)` — every block is present; the yield is genuinely zero, not
missing. **The discriminator is that `BplusBcminus` passes in that same bin**: B_c
*is* populated in the top class for a B⁺ trigger, so what is empty is
specifically the **beauty-baryon + B_c combination** at 10M events. HF_RUN3_V1 is
**10× larger** — 100M events per tune against HF_PT2_INT's 10M.

> **THE INDEX INVERSION**, recorded in the config itself and repeated here
> because reading it the wrong way descopes the only bin B_c populates:
> **`M0_1` is the TOP class** (0–1 % = highest multiplicity, `Model.tex:126`),
> **but the memo's `c1…c11` runs the opposite way** — memo **`c11` ↔ `M0_1`
> (highest)**, memo **`c1` ↔ `M90_100` (lowest)**.

**The check stays strict.** `positive_required` is **not** weakened, in either
direction, and the audit's zeroing of `subsample_error_bins_to_exclude` stands.
B6 closes on the finding being *characterised and attributed*, not on the audit
being made to pass.

**RECORDED FOLLOW-UP — not deferred silently.** Re-run both targets against
HF_RUN3_V1 once its v3 analysis converges and merges. **Green ⇒ the statistics
reading is confirmed and nothing further is owed.** **Still failing at 10× ⇒ it
returns to the owner as a physics-scope decision** — G2's top-class retention
would not hold for beauty-baryon triggers, and that pair's scope should be
integrated-only. **Owner decision; do not weaken `positive_required` in either
case.**

**Pre-registration miss, recorded as such:** the prediction was that descoping
would make the audit pass outright. It did not — descoping removes the
*out-of-scope* failures, not *all* of them, because G2 **retains** the top class
and one pair is empty even there. The miss located the residual precisely.

### B7. The generator hang is a production planning number, not a footnote
8 of 300 intermediate-campaign jobs (**2.7 %**) hit `HF_HANG_GUARD`:
**5 JUNCTIONS, 3 CLOSEPACKING, 0 MONASH.** Not a defect — the guard worked —
but it must be budgeted.

**The distribution is the interesting part, not the rate.** HF_PT2's single hang
was also JUNCTIONS (`submit_HF_PT2_retry5.sub`, section 2). Across two
campaigns, **every hang so far has been a colour-reconnection tune and none has
been MONASH.** Under a null of tune-independence, 8/8 landing on the two CR
tunes has probability (2/3)^8 ≈ 3.9 % — suggestive, not conclusive, and it does
not account for the CR tunes' longer CPU (`Makefile:33-37`: MONASH 247 s median,
JUNCTIONS 480 s, CLOSEPACKING 677 s), which raises their exposure to a
fixed 3600 s CPU guard independently of any hang mechanism. **That confound has
to be separated before the pattern means anything** — the honest statement today
is "consistent with both a CR-specific hang and with plain CPU exposure".

#### MEASURED — they hung; they were not merely slow

Held-job CPU, all 8: **3608-3610 s** (one CLOSEPACKING at 3896 s), CPU/wall
**0.992-0.997**.

Completed-job CPU from this same campaign (`condor_history 5319282`, n=292,
same binary, same 100k events/job):

| Tune | n | mean | **max** | held / max |
|---|---|---|---|---|
| MONASH | 100 | 377 s | 649 s | — (none held) |
| JUNCTIONS | 95 | 659 s | **1046 s** | **3.45x** |
| CLOSEPACKING | 97 | 989 s | **1387 s** | **2.60x** |

**Verdict: genuine hangs. Retry is the correct response; a proportional
per-tune guard is not the remedy for these 8.**

Two things carry the argument, and note that **CPU/wall does not** — a hung
generator and a healthy compute-bound job both run near 100 % CPU, and every
guard kill lands at ~3600 s by construction, so neither number discriminates:

1. **Magnitude.** 2.6-3.5x beyond the observed maximum of their own tune's
   completed distribution, over 95-97 samples each.
2. **Bimodality, which is the decisive one.** There is a clean empty gap
   between 1387 s (slowest completed job, any tune) and 3600 s (the guard).
   A heavy tail would have populated it — some jobs finishing at 1600 s,
   2200 s, 2800 s. Nothing did. The held jobs are a separate population, not
   the upper tail of the healthy one.

#### Side finding: the Makefile's recorded CPU figures are stale and low

`Makefile:36-38` records MONASH 247 s median / 321 s max, JUNCTIONS 480 s /
632 s, CLOSEPACKING 677 s / 762 s. **Measured here: means are 1.4-1.5x those
medians and maxima are 1.6-1.8x those maxima.**

This matters for guard sizing at production scale, and it cuts the other way
from the verdict above: CLOSEPACKING's real headroom against the 3600 s guard
is **2.6x** (1387 s observed max), not the ~4.7x the stale comment implies.
That is thin enough that a genuinely slow CLOSEPACKING job could be killed as
collateral at 3000 jobs. **A proportional per-tune guard is still worth
considering for production — just not as the remedy for these 8.**

#### The full-production CPU budget is wrong by 1.44x

At the measured means, 1000 jobs/tune x 100k events:

| Tune | measured mean | CPU-hours @1000 jobs | stale figure |
|---|---|---|---|
| MONASH | 377 s | **104.7** | 68.6 |
| JUNCTIONS | 659 s | **183.1** | 133.3 |
| CLOSEPACKING | 989 s | **274.7** | 188.1 |
| **Total** | | **562.5 CPU-h** | **390.0 CPU-h** |

**~562 CPU-hours, not ~390.** Note: `grep` finds **no occurrence of 390
anywhere in the tracked tree** — it has been quoted verbally but never written
down, so there is nothing to correct in place. **Write 562.5 down** (with the
per-tune breakdown) rather than only fixing `Makefile:36-38`, or it will drift
back. Excludes hang overhead, below.

#### Per-tune guard — MOVED TO `POST_SUBMISSION.md`

Owner's decision, 2026-08-05, on the measured tail below: the flat 3600 s guard
is **not** killing healthy jobs, so this is production hygiene rather than a
blocker. The full proposal and its justification now live in
`POST_SUBMISSION.md`.

**Still wanted before production:**

1. ~~Is the concentration significant once CPU exposure is accounted for?~~
   **Partly answered.** The hangs are real, and the CR tunes' 1.7-2.6x higher
   baseline CPU does not explain a 2.6-3.5x overshoot. Whether CR tunes are
   *intrinsically* more hang-prone, or merely more exposed, still needs the
   MONASH hang rate to be non-zero somewhere to compare against — across two
   campaigns it remains exactly 0.
2. At 3000 jobs: ~80 held, concentrated in two tunes, all needing retry to land
   on **exactly 1000 each** (B1 of the chain: `build_canonical_manifest.py:119`
   and `:128` refuse anything else).
3. **Does `tools/resubmit_held.py` handle a batch of ~80 cleanly?** Unverified.
   It has only ever been exercised on batches of 1 (HF_PT2 retry5) and,
   historically, 38 (`submitCondor_hf_90M_resubmit_4181781_held38.sub`).
4. **How many retry rounds does convergence take, and how many seeds does that
   burn?** A retried job can hang again. If the hang is CR-specific and
   seed-independent, round 2 hangs at a similar rate and the tail is
   geometric: ~80, then ~2, then ~0 — two or three rounds. If it is
   seed-specific, one round suffices. **These predict different multi-day
   tails, which is the thing worth knowing now rather than discovering.**
   Note `MAX_ATTEMPTS = 10` (`campaign.py:69`), so attempts are not unlimited.

Interacts with B2: **resubmission burns seeds while the original submit does
not** — the inverse of what you would want.

### B9. `resubmit_held.py` hardcodes campaign ordinal 1 — CLOSED, evidence `e403853`

> **CLOSED 2026-08-09 on verification. Fixed by commit `e403853`.** The literal
> is gone. `tools/resubmit_held.py` now derives the ordinal from the campaign it
> is completing: `campaign_ordinal_on_disk()` at **`:71-89`** reads
> `campaign_ordinal` from the on-disk attempt sidecars;
> **`--campaign-ordinal` defaults to `None`** (`:99-100`) and exists only for the
> case derivation cannot cover; derivation plus a **refusal when a campaign
> carries more than one ordinal** runs at `:136-145`.
>
> **Covered by a test that pins the property, not the flag:**
> `tests/test_resubmit_held_ordinal.py` — derivation, refusal on disagreement,
> refusal on a contradicting override, and "underivable" kept distinct from "1".
> **It is one of the 24 in the green local suite.**
>
> The original text is kept below for the record.

`tools/resubmit_held.py:171` passes `"--campaign-ordinal", "1"` as a literal,
with no CLI option and no way for a caller to override it.

**Any campaign not using ordinal 1 gets retries stamped with the wrong
ordinal.** The campaign ordinal is packed into the event ID, so a retried job
produces events attributed to a different campaign from the ones it is
completing — inside a single merge.

Latent since the tool was written; every prior campaign (`HF_SMOKE`,
`HF_SMOKE2`, `HF_PT2`) used ordinal 1, so it never fired. `HF_PT2_INT` is
ordinal 2 and exposed it immediately.

**Worked around, not fixed** (Nikhef frozen mid-campaign): the retry was
rendered directly with `--campaign-ordinal 2 --only-jobs <the 8>`, which is the
same code path the tool invokes internally. **Fix in the first post-sync
commit, alongside B2** — add `--campaign-ordinal` with default 1 and thread it
through, or derive it from the campaign's existing manifest rather than
accepting it as an argument at all (**preferable: it cannot then disagree with
the campaign it is completing**).

**Hazard left on disk:** `/data/alice/ipardoza/Hadronization/submit_HF_PT2_INT_retry7.sub`
carries the wrong ordinal and was never submitted. It survives because the
renderer's write-once guard correctly refused to overwrite it and nothing is
deleted without approval. **Do not submit it.**

### B8. Which tree does the paper's reproducibility statement point at?
**Nobody has raised this and it is invisible in every prior handoff.**

`main` and `physics-focus` have diverged enormously. `main` (the collaborator
PR-merge branch, at `11884cf`) contains **none** of this infrastructure — no
`Makefile`, no `tools/`, no `docs/`, no `REPRODUCIBILITY.md`, no `Validation/`.
`physics-focus` (at `e690e17`) is where every validator, campaign tool and
figure-producing macro lives, and is what produced all merged data.

A methods section saying "the code is at github.com/..." has to resolve to the
tree that produced the figures. Options are merge `physics-focus` into `main`,
replace `main` with it, or publish from `physics-focus` — **an owner decision,
not proposed here.** What must not happen is that it stays undecided until
submission.

#### B8b. The paper is untracked by git — part of this blocker, not adjacent to it

**The manuscript itself is in no branch's index.** It lives at
`Paper/Heavy_flavour_hadronisation_model_paper/` inside the **`main`** worktree
and `git ls-files --error-unmatch` fails on it. Seven `.tex` files, 589 lines,
existing only on one laptop.

This belongs *inside* B8 rather than beside it because it is the same defect one
level down: a reproducibility statement cannot point at a directory that exists
only on one machine, and resolving the branch question does not resolve this one
— merging `physics-focus` into `main` would still leave the paper untracked.

Both halves have to be answered together: **which tree do we publish from, and
is the manuscript in it.** Note there is a plausible innocent explanation —
the paper may be synced by hand from Overleaf, in which case tracking it in git
is the wrong fix and the right one is recording where the authoritative copy
lives. That cannot be determined from the tree; it is a question for the owner.

### B10. The serial checksum gate is on the submission path too, not only the merge

**Precondition 10 was written as though the merge were the only stage that
sha256s the whole dataset serially. It is not.** `merge_root_files.sh:81`
runs `tools/validate_analysis_outputs.py` as its first gate, and
`submit_status_analysis.sh` runs the same class of work *before queueing a
single analysis job*. The analysis submission of 2026-08-05 validated 300
files (~29 GB) that way — the session that ran it recorded the cost as "well
over an hour" but did not instrument it, so it produced no number.

**So "move it to Condor" applies to the analysis submission path as well.**
At 3000 files this is on the order of 15-20 hours *before the first job is
queued*, on a login node, single-threaded, ahead of any work that could be
parallelised. Nobody had stated this; it was invisible while the only stage
anyone timed was the merge.

#### First instrumented data point

Measured this session, run directory
`/data/alice/ipardoza/merge_runs/HF_PT2_INT_run01` on `stbc-i3`
(`merge.log`, `rss_samples.log`, `run_meta.txt` retained):

| | |
|---|---|
| Gate | `validate_analysis_outputs.py`, 300 analysis directories, ~29 GB |
| Started | epoch 1785890527, immediately after `CANONICAL_MERGE_SHAPE` |
| Ended | epoch 1785894881, `ANALYSIS_OUTPUT_MANIFEST_VALID status=PASS directories=300 missing=0` |
| **Duration** | **4354 s = 1 h 12 m 34 s** |
| CPU / wall | **0.050** (165 s CPU at t=3269 s) — I/O-bound |
| RSS | **18.4 MB** (the validator's own, read from `/proc`) |

**The extrapolation, now that both ends are real numbers.** 300 files in
4354 s, scaling linearly, puts 3000 files at **~43,500 s ≈ 12.1 hours before a
single analysis job is queued.** That sharpens the previous session's "on the
order of 15-20 hours" to a measured ~12, and it is still long enough that
precondition 10 stands: **this belongs on Condor.**

**Its CPU cost is not the problem.** At CPU/wall = 0.05 the gate spends ~2200 s
of CPU at 3000 files, against the 115200 s per-process ceiling — two orders of
magnitude clear. **What needs moving is the wall-clock, and the reason is that
it is serial and blocking, not that it is expensive.**

#### SUPERSEDED 2026-08-08 — the gate is CPU-BOUND. Every 0.050-derived line above and below is void

**The `CPU / wall = 0.050` row, the "I/O-bound" label, the ~2200 s CPU figure
and the "two orders of magnitude clear" claim are all superseded.** They are
retained above so the reasoning stays auditable, not because they stand.

**Method.** A standalone P=1 reference ran the **unmodified** gate with
`--report` omitted (so it wrote nothing — see the `--report` hazard), detached,
uncontended on `stbc-i3` (62 cores, loadavg 0.40 at launch), under
`/usr/bin/time`. Artifact retained at
`/data/alice/ipardoza/poolsweep_run01/p1_time.txt`; see also
`docs/REGISTRY_AND_MAPPING_PROPOSAL.md` §0b.

```
P1_TIME wall=4156.96 user=3612.88 sys=205.17 maxrssKB=451480 cpupct=91%
```

| | recorded above | measured P=1 |
|---|---|---|
| wall @ 300 dirs | 4354 s | **4156.96 s** — agrees to 4.5 % |
| CPU (user+sys) | ~165–220 s | **3818.05 s** |
| **CPU/wall** | **0.050** | **0.919** |

**Wall agrees; CPU disagrees by a factor of ~23.** Same work, same wall — so
**the 0.050 figure was wrong at its origin.** It was a mid-run sample
(`165 s CPU at t=3269 s`) that measured the Python parent and **missed the ROOT
children the gate spawns per directory** at `tools/validate_analysis_outputs.py:506`.

**Corrected projection, with method.** Tree CPU **3818 s at 300 directories**,
scaling linearly → **≈ 38,200 s at 3000**. Wall at P=1 → **≈ 41,570 s ≈ 11.5 h**
(the ~12.1 h wall figure above survives; only its CPU companion does not).

#### B10's closure SURVIVES the correction — and the reasoning gets simpler

**The blocker's conclusion is unchanged. What changes is why.**

- **The units are 300 independent per-directory validations** — the **same
  shape as the merge phase**, not the opposite one. The earlier framing
  (gate = latency-bound, merge = CPU-bound, "different remedies that must not
  share a fix") is **wrong on the gate half**; both fan out because their units
  are independent.
- **The pool remedy stands.** Independent CPU-bound units parallelise across
  cores at least as well as latency-bound ones. The remedy was right for the
  wrong reason.
- **The per-process ceiling still does not bind.** The correct comparand is a
  **single ROOT child**, not the 3818 s tree total. Each child validates one
  directory and is far below 115,200 s. **`ulimit -t` is per process; the tree
  sum is the wrong number** — the same scope error retracted earlier in this
  blocker.
- **The contract obstacle is untouched:** `validate_analysis_outputs.py` still
  writes one report that `merge_root_files.sh:80-84` consumes, so *sharding*
  remains a contract change while *pooling* does not.

**`maxrssKB=451480` (441 MB), with its method.** `/usr/bin/time` reports max
RSS from `rusage`, which for descendants is the **largest single waited-for
descendant, not the sum** — so this is almost certainly **one ROOT child**, not
the Python parent. **Hypothesis only, not established:** this plausibly
reconciles the 437 MB sampler figure recorded elsewhere in this blocker (441 MB
vs 437 MB, within 1 %), which would mean that number was also a ROOT child
rather than the validator. **The validator's own 18.4 MB, read from `/proc`,
is a different and still-valid measurement of a different process.**

#### THE THREE MEASUREMENTS — taken 2026-08-05, run01

| # | Measurement | Result |
|---|---|---|
| 1 | Merge peak RSS at 100 inputs | **717 MB** (734,652 kB, kernel `/usr/bin/time -v`). **2.85x headroom under the 2.00 GiB login cap.** Sampled attribution: 663 MB during the first central, 692 MB across block stages |
| 2 | Merge wall-clock at 300 inputs | **gate 1 h 12 m 34 s + merge 2 h 16 m 12 s = 6 h 44 m 37 s total.** Baseline 61 m 45 s at 30 inputs |
| 3 | `inputs_per_block = 10` closure at 2e-10 | **HOLDS — all three tunes.** `errors=0`, 1800 sumw2 checks, 3600 additive-metadata, 600 invariant-metadata, 300 source-filter, `relative_tolerance=2e-10`. MONASH from the merge run; JUNCTIONS (3669 s) and CLOSEPACKING (3764 s) re-run separately after `exit 7` blocked them. The `exit 7` is B12, a stale literal — **not a closure failure** |

**Measurement 1 must be read against its provenance caveat** (below): 717 MB is
the whole process tree at 100 inputs; the 450 MB baseline was one pair file at
10 inputs from a deleted harness. Not commensurable. What the number does
establish on its own terms is that the merge fits under the strict login-node
cap with 2.85x to spare.

**Prediction at 1000 inputs: roughly flat, ~700-800 MB.** The reasoning, so
full production tests a stated expectation rather than discovering one. With
the `TH1::AddDirectory(kFALSE)` ownership fix in place the per-input objects are
transient — fetched, added, freed — and the only retained structure is the
merged clone, which is **histogram-sized and therefore independent of how many
events were summed into it**. THnSparse is the one thing that could break this:
it stores filled bins, not a fixed grid, so a tenfold increase in statistics
fills bins that ten times fewer events left empty. That growth is sub-linear
and saturating (bins fill up and stop being new), so the expectation is a
modest rise, not 10x. **Falsification: a peak near 7 GB at 1000 inputs would
mean inputs are being retained and the leak is back.** Note the sampled
attribution already shows block stages (10 inputs) peaking at 692 MB against
the first central's (100 inputs) 663 MB — near-flat across a tenfold input
difference, which is the same prediction holding at the scale available now.

#### THE CPU CEILING — RETRACTED PENDING DECOMPOSITION, twice invalid

**The "2.04x over the ceiling" verdict below is not safe to act on. Two
independent errors, both mine, both found by owner challenge.**

**Error 1: the per-directory table is not a merge-macro cost.** It was derived
from `PROMOTED_MERGE` log-line timestamps, and that line is echoed at the *end*
of `merge_one()`. Each window therefore spans the macro **plus**
`validate_pair_directory.sh` over 300 output files, `merged_pair_provenance.py
write`, a **second** directory validation, `provenance validate`, and the
guarded `mv`. MONASH's window additionally starts at gate-end, absorbing
everything between the gate finishing and the first merge starting. **7728 s is
a `merge_one()` window, not a macro cost, and must not be compared with the
scaling series, which times `MergeCanonicalAnalysis.C` alone under
`/usr/bin/time`.** The apparent 22x gap is scope. This is the third scope error
in this project — after the 437 MB sampler and the 450 MB harness — and the
pattern is now explicit: **before comparing two numbers, establish that they
measure the same thing.**

**Error 2: tree CPU compared against a per-process limit.** `/usr/bin/time -v`
sums CPU across the whole process tree; `ulimit -t` is enforced **per process**.
The merge phase ran **8172 s wall against ~23,284 s CPU — a ratio of ~2.85**, so
roughly three cores were busy on average and the tree is demonstrably parallel.
**The number to test against 115,200 s is the largest single process's CPU, not
the tree total**, and that is smaller by an unknown factor.

**Consequence, and it may remove the blocker entirely.** The 65 h projection
assumed all 23,502 s scales linearly with input count. It probably does not: the
output directory is 300 pair files regardless of inputs, because the objects are
histograms, so directory validation, provenance and promotion are **fixed in
output size**. Early scaling points put the macro at ~37 s for 10 inputs; if a
100-input central is ~350 s, the macro across the whole run is roughly
`3 x 350 + 30 x 37 ~ 2100 s` — **under 10 % of merge-phase CPU**. At 1000 inputs
the macro term grows tenfold while the dominant fixed term does not, giving
**~12 h rather than 65 h**. **If that holds, the merge needs no split and B10's
merge half shrinks from a redesign to a note**, leaving only the gate's 12 h —
which already fans out trivially.

**What settles it, in order:** (1) let the remaining scaling points bound the
macro term; (2) decompose one central directory's window into macro, both
directory validations, both provenance steps and promotion; (3) label each term
as input-scaling or output-fixed; (4) take the largest **single-process** CPU and
compare that against 115,200 s. **Do not re-quote 65 h, 2.04x, or "cannot
complete full production" until those four are done.**

#### ALL FOUR CHECKS COMPLETE — 2026-08-05. THE CEILING DOES NOT BIND

**The retraction is lifted and replaced with a positive statement.** Evidence in
`docs/handoffs/HANDOFF_20260805_v8.md` §2–§5.

| # | check | result |
|---|---|---|
| 1 | macro term bounded | 8-point scaling series, `/usr/bin/time`. `macro(MONASH,100) = 6449.42 s` wall, **6362.98 s CPU** |
| 2 | one central window decomposed | JUNCTIONS central, from the **real run's** timestamped `merge.log`; parts sum to **1613 s** exactly. CLOSEPACKING sums to **1533 s** |
| 3 | each term labelled | macro **input-scaling**; both validations, both provenance steps and `mv` are **output-fixed** (300 pair files regardless of input count) and are **79 %** of the window |
| 4 | largest single-process CPU | **the macro, 6362.98 s** — see the bound below |

**Check 4 closes by bound, not by measurement.** `CPU <= wall` always, so no
process can exceed its own window. The largest non-macro window is validation #1
at **644 s**; validation #2 is 634 s, provenance write 11 s, validate 5 s,
promotion 0 s. All are an order of magnitude below the macro's 6362.98 s CPU, so
**the macro is the largest single process** and no assumption about their
CPU/wall ratios is required. This also disposes of the concern that validations
#1 and #2 read different directory states — both are bounded by their own
windows without assuming the two match.

#### The projection at 1000 inputs, with both models stated

`ulimit -t` is **115,200 s (32 h) per process**, and each `merge_one()` spawns
its own `root.exe` (confirmed by direct measurement, PIDs 3311652 and 3227874),
so the per-directory macro is the correct comparand.

| model | basis | CPU at 1000 inputs | fraction of ceiling |
|---|---|---|---|
| **Pessimistic** | everything linear from 100 | 6362.98 x 10 = **63,630 s = 17.7 h** | **55 %** |
| **Measured decomposition** | baseline linear + excess as sqrt(N) | 343.17 x 10 + 6019.81 x sqrt(10) = **22,468 s = 6.2 h** | **19 %** |

The second model rests on the measured separation of MONASH into a
JUNCTIONS-like baseline plus an excess scaling as **sqrt(N) to within 1.1 %**
(`POST_SUBMISSION.md`, "The MONASH 49x merge step"). **Both figures are given
because the conclusion does not depend on choosing between them** — the ceiling
does not bind under either reading, and this project's recurring failure has
been numbers quoted without their provenance.

#### HOW THIS BLOCKER-HALF WAS CLOSED — read this before trusting the demotion

**B10's merge half was closed by measurement and bound, NOT by a code change.
This is the first time a blocker on this list has been closed on analysis rather
than on a fix, and the distinction is load-bearing.**

**No behaviour was altered. No file in the pipeline was touched. `merge_one()`,
`MergeCanonicalAnalysis.C`, `MergeAnalysisObjects.C` and
`validate_pair_directory.sh` are byte-identical to what they were when the
blocker was opened.** What moved is the *projection*: the original verdict rested
on two scope errors (a `merge_one()` window read as a macro cost, and tree-wide
CPU compared against a per-process `ulimit -t`), and correcting those — plus
bounding the macro term against a real ceiling — removed the problem that was
being solved for. **The pipeline was always fine; the number describing it was
not.**

**The practical consequence of that distinction:** there is no fix to verify, no
regression to guard, and no test that can pin this closed. **What keeps it
closed is the evidence above.** If any of those measurements is superseded, this
half of B10 reopens on its own terms.

**Consequences:**

- **B10's merge half reduces to a note** recording this projection and its two
  bounds. It is no longer a structural requirement.
- **The gate's ~12 h is untouched and remains the real problem.** It is
  ~~latency-bound (CPU/wall 0.050)~~ **CPU-bound (CPU/wall 0.919, measured
  2026-08-08 — see the SUPERSEDED block above)**, embarrassingly parallel
  because its 300 directory validations are **independent**, and the P=8-16
  pool remedy is costed below **but needs re-baselining**. **The two halves of
  B10 are still asymmetric — only the gate has a defect and only the gate has a
  remedy pending — but they are asymmetric in *status*, not in *profile*: both
  stages are CPU-bound and fan out for the same reason.**

**CONDITIONAL — per-directory invocation is sufficient, PROVIDED
`merged_pair_provenance.py` holds no cross-directory state.**

This is a **condition on the claim, not a footnote to it.** The reasoning that
`merge_one()` can be invoked per directory rests on it being self-contained:
it makes its own stage via `mktemp`, runs its own validation and provenance
write/validate, and promotes under a guard (`merge_root_files.sh:167-183`), with
the freeze manifest, the blocks and the analysis report **read-only** to every
invocation. `merge_root_files.sh` was read in full and satisfies this.
**`merged_pair_provenance.py` was not audited.**

**If that audit finds cross-directory state, the per-directory conclusion needs
revisiting and this demotion is not final.** The ceiling arithmetic above is
unaffected either way — it is a per-process CPU bound and does not depend on the
invocation shape — but "no split required" does. **The audit is first on the
next session's queue precisely so this becomes unconditional.**

#### AUDIT DONE 2026-08-06 — THE CONDITION ABOVE IS DISCHARGED. UNCONDITIONAL

**`merged_pair_provenance.py` holds no cross-directory state. "No split
required" is now unconditional.**

**Writes — three, all inside the invocation's own `directory`, `write`
subcommand only:** `source_manifest.jsonl` (`:277`), `merge_provenance.json`
(`:297`), `merged_pair_checksums.json` (`:305`). **No write of any kind outside
`directory`. No shared, aggregate or index file anywhere.** `validate` writes
nothing at all.

**Reads outside `directory` — all read-only, and all already covered by B10's
"shared inputs are read-only" premise:** the per-invocation `manifest`;
`checkout/AnalysisScripts/GeneratedPairRegistry.h` (`:59`),
`MergeCanonicalAnalysis.C` (`:291`), `MergeAnalysisObjects.C` (`:294`); the
`analysis_report` (`:126`); `freeze_dir/canonical_manifest.jsonl` (`:127,132`),
`freeze_seal.json` (`:150`), `canonical_raw_validation_receipt.json` (`:153`,
optional); and `git rev-parse HEAD` (`:214,287`), `merge-base --is-ancestor`
(`:217`), `git show <commit>:<path>` (`:243`). **Git is read-only throughout,
and concurrent git readers are safe.**

**No other merged directory is ever touched.** Every directory traversal —
`:173`, `:181`, `:269` — is `directory.iterdir()` on the single invocation
target. No glob over `hadronization_merged`, no parent or sibling traversal, no
path built from anything but the `directory` argument.

**No ordering dependency between directories.** The only pre-existing-state
check is `:274-276`, refusing to overwrite the three sidecars **in its own
directory** — within-directory idempotence, not cross-directory state.

**Verified by execution, not only by reading.** Two `validate` invocations run
**concurrently on different promoted directories**:

```
[JUNCTIONS]    MERGED_PAIR_DIRECTORY_VALID tune=JUNCTIONS inputs=100 files=300
[CLOSEPACKING] MERGED_PAIR_DIRECTORY_VALID tune=CLOSEPACKING inputs=100 files=300
```

wall 9.27 s and 10.48 s. **Sidecar mtimes and sizes were byte-identical before
and after**, confirming `validate` is read-only in fact and not only by
inspection.

**Scope of the empirical test, stated:** concurrency was exercised on
`validate`, not `write`. `write` was audited by inspection plus a disjointness
argument — its only three write targets are inside its own `directory`
(`:277,297,305`) and it refuses to overwrite (`:274-276`), so two `write`
invocations on different directories have disjoint write sets by construction.
**`write` was deliberately not run concurrently: it creates files, and the only
directories available to test against are promoted data.**

**One property recorded because it looks like cross-directory state and is
not:** `source_manifest_scope` (`:86-114`) requires the manifest to contain
**all three tunes with equal per-tune counts**
(`len(rows) == len(TUNES) * input_count`). That is a cross-*tune* constraint on
a **read-only input file**, not cross-*directory* state, and it does not impede
parallel invocation.

#### Measurement 2 — RELABELLED, not retracted

"gate 1 h 12 m 34 s + merge 2 h 16 m 12 s = 6 h 44 m 37 s" does not add. **The
total is correct; one label is wrong and a third term was never named.** From
`run_meta.txt` (`MERGE_RUN_START 1785890525`, `MERGE_RUN_END 1785914804`):
gate **4354 s** + 33 merge windows **15,900 s** + closure **4023 s** =
**24,277 s = 6 h 44 m 37 s**. And `15,900 - 7,728 = 8,172` exactly — the
"2 h 16 m 12 s" figure is **the merge phase with MONASH's central window
excluded**. Closure verified at `merge.log:1044` (`PAIR_BLOCK_CLOSURE errors=0`,
`relative_tolerance=2e-10`); the `exit 7` at `:1046` is B12's stale literal, not
a closure failure.

#### The retracted verdict, kept for the record

**Superseded by the two errors above. Retained so the reasoning is auditable,
not because it stands.**

| | |
|---|---|
| CPU (user+sys) | **23,502 s = 6 h 31 m 42 s** |
| wall | 24,277 s |
| **CPU/wall** | **0.97 — CPU-bound** |
| projected at 3000 inputs | **235,022 s = 65 h 17 m** |
| `ulimit -t` | 115,200 s (32 h) |
| **ratio** | **2.04x OVER THE LIMIT** |

**The merge stage is CPU-bound at 97 %, the opposite of the gate.** Waiting
longer cannot help: the process would be killed at 32 hours, roughly half way.
**B10 is therefore not a wall-clock convenience for the merge — it is a hard
structural requirement.** The merge must be decomposed before full production
can complete at all.

**The gate and the merge need different remedies and must not share a fix.**
The gate is **latency-bound at CPU/wall 0.050**; the merge is **CPU-bound at
0.97**. Fanning the gate out attacks per-file round-trips; splitting the merge
attacks CPU that one process cannot spend inside 32 hours. Same direction,
different problems.

> **SUPERSEDED 2026-08-08.** The gate is **CPU-bound at 0.919**, measured. The
> two stages have the **same** profile and fan out for the **same** reason —
> independent units — not opposite ones. See "SUPERSEDED — the gate is
> CPU-BOUND" above.

#### Splitting the merge — the arithmetic, measured

Per-directory wall time from this run's `PROMOTED_MERGE` timestamps:

| Directory | inputs | wall |
|---|---|---|
| `complete_root_..._MONASH` | 100 | **7728 s** |
| `complete_root_..._JUNCTIONS` | 100 | 1613 s |
| `complete_root_..._CLOSEPACKING` | 100 | 1533 s |
| 30 blocks | 10 each | 5026 s total, mean 168 s, max 190 s |

Centrals are **68 %** of the merge, blocks 32 %.

**At 1000 inputs, scaling linearly, the largest single directory is the
binding case:** 7728 s x 10 x 0.97 CPU/wall ≈ **20.8 h CPU**, against the
115,200 s (32 h) ceiling — **it fits, but at 1.5x, not comfortably.** A typical
central (JUNCTIONS, 1613 s) projects to ~4.3 h and is never at risk. **So
"invoke per directory" is a sufficient remedy, and no redesign is needed —
but the margin on the worst directory is 1.5x and should not be spent.**

**MONASH's central is 4.8x the other two for identical input counts, and that
is unexplained.** It is the first directory merged, so first-invocation effects
(cling JIT, cold cache) are candidates, as is MONASH's genuinely denser
meson-meson content. **It is also exactly the directory that sets the ceiling
margin, so the cause matters.** Not investigated here.

**Does splitting need a contract change? No — and this is the difference from
the gate.** `merge_one()` is already self-contained per directory: it makes its
own stage via `mktemp`, runs its own `validate_pair_directory.sh` and
`merged_pair_provenance.py write/validate`, and promotes with `mv` under a
"final directory appeared before promotion" guard. The shared inputs — the
freeze manifest, the blocks, and `analysis_output_manifest_validation.json` —
are **read-only** to every invocation. The closure runs afterwards over
promoted directories and is indifferent to how they were produced. Contrast
the gate, where `validate_analysis_outputs.py` **writes** the single report
`merge_root_files.sh:80-84` consumes, so sharding it changes a contract.
*Limit of this claim:* I read `merge_root_files.sh` in full but did **not**
audit `merged_pair_provenance.py` for cross-directory state; that should be
confirmed before the split is implemented.

#### The gate remedy, costed — ~~it is latency-bound, which is why fanning out works~~

> **SUPERSEDED 2026-08-08 — the premise of this whole subsection is wrong, the
> recommendation is not.** The gate is **CPU-bound at 0.919**. "Latency-bound
> work is exactly what parallelism fixes" is void as stated: the work is
> **CPU**, and it parallelises because the 300 directory validations are
> **independent**, not because fan-out hides I/O waits. The pool is still the
> right remedy. See "SUPERSEDED — the gate is CPU-BOUND" above.

**The bottleneck is per-file latency, not bandwidth.** 300 directories x 300
pair files = **90,000 files in 4354 s = 20.7 files/s, i.e. ~48 ms per file**,
moving 29 GB at an effective 6.7 MB/s. That is nowhere near the shared
filesystem's throughput; it is the round-trip cost of opening and hashing many
small (~40 kB) files in sequence. **Latency-bound work is exactly what
parallelism fixes** — unlike a bandwidth-bound stage, where fan-out would just
redistribute the same saturated pipe.

Per-directory checksums have **no cross-dependence**, so the shape is a plain
map-reduce over directories:

| Shape | Wall clock at 3000 dirs | Peak RSS | Notes |
|---|---|---|---|
| today: 1 process | **~12.1 h** | 18.4 MB | serial, blocking, on a login node |
| local pool, P=8 | **~1.5 h** | ~150 MB | fits even under the 2.00 GiB login cap |
| local pool, P=16 | **~45 min** | ~300 MB | still 7x under the login cap |
| Condor, 100 jobs x 30 dirs | **~7 min/job** | 18.4 MB/job | plus queue latency and a reduce step |
| Condor, 300 jobs x 10 dirs | **~2.4 min/job** | 18.4 MB/job | queue overhead starts to dominate |

**Recommendation: the bounded local pool, P=8-16.** It converts the single
largest post-production wait from 12 hours to under an hour, needs no queue,
no per-shard receipt protocol, and stays far inside the *login-node* cap at
18.4 MB per worker. **The Condor fan-out is the better answer at full scale
only if the reduce step is built**, because `validate_analysis_outputs.py`
currently writes **one** report
(`analysis_output_manifest_validation.json`) that the merge then consumes at
`merge_root_files.sh:80-84`; sharding it means emitting per-shard receipts and
combining them into a byte-identical whole, which is a contract change, not a
scheduling change. **That cost is the reason to start with the pool.**

*Unverified:* the P values above assume near-linear scaling from the
latency-bound argument. That follows from the measurement but has not been
demonstrated — **run the pool at P=4 and P=8 over the existing 300 directories
and confirm the slope before quoting these numbers for full production.**

> **SUPERSEDED 2026-08-08 — the P-scaling table above is NOT quotable and its
> ceiling has changed.** Two corrections:
>
> 1. **The scaling argument was latency-based and that premise is void.** The
>    work is CPU-bound at 0.919, so speed-up is **bounded by available cores**,
>    not by how many outstanding I/O requests can be kept in flight. P=16 on a
>    62-core host is plausible; the same P on a loaded or smaller host is not.
>    **The table needs a re-baseline against the measured P=1 before any value
>    is quoted.**
> 2. **The P=1 row is now measured, not projected:** wall **4156.96 s** at 300
>    directories (the table's 12.1 h at 3000 is a linear extrapolation of the
>    superseded 4354 s; the measured equivalent is **≈ 11.5 h**).
>
> The P=4/P=8 sweep the paragraph above asks for **is still the right next
> step** — and it is now the *only* way to get the slope, since the analytic
> latency argument that stood in for it no longer holds. **Not blocking:
> whether the pool exists changes when figures appear after production, not
> whether production can start.**

**The RSS number matters more than it looks.** 437 MB at 300 files, and it
does not grow as the gate proceeds — the validator streams rather than
accumulating. So this stage is I/O-bound and does *not* scale its memory with
the dataset; at 3000 files it will take ten times as long and use the same
memory. The thing to move to Condor is wall-clock, not footprint.

> **PARTIALLY SUPERSEDED 2026-08-08; RSS ATTRIBUTION NOW MEASURED 2026-08-09.**
> The **flat-with-dataset-size** claim stands and is the load-bearing half —
> P=1 measured **maxrssKB=451480 (440.9 MiB)** at 300 directories, consistent
> with 437 MB. **The "so this stage is I/O-bound" inference is void**; memory is
> flat because the validator streams, which says nothing about where the time
> goes, and the time is CPU.
>
> **The attribution is no longer a hypothesis.** A dedicated `/usr/bin/time -v`
> run of one `validate_pair_directory.sh` against a promoted directory, on a
> batch node, uncontended, artifact
> `/data/alice/ipardoza/poolrss_run01/time_v.txt`:
>
> ```
> Maximum resident set size (kbytes): 584452        # 570.8 MiB
> User time 650.08 s   System time 0.84 s   Elapsed 10:54.07   Percent of CPU 99%
> ```
>
> **A single ROOT-based directory validator uses 570.8 MiB at 99 % CPU.** The
> 18.4 MB figure is the Python orchestrator and **cannot be the per-worker
> footprint**. Both 437 MB and 441 MB are ROOT children, as suspected.
>
> **THE RSS COLUMN IN THE POOL TABLE ABOVE IS WRONG BY ~24x, AND THE "fits
> even under the 2.00 GiB login cap" CLAIM INVERTS.** Against the 2048 MiB
> login-node cap:
>
> | pool | per-worker | P=4 | P=8 | P=16 |
> |---|---|---|---|---|
> | **gate** (`validate_analysis_outputs.py` child) | **440.9 MiB** | 1764 MiB — fits | **3527 MiB — EXCEEDS** | 7054 MiB — exceeds |
> | **merge-side** (`validate_pair_directory.sh`) | **570.8 MiB** | **2283 MiB — EXCEEDS** | 4566 MiB — exceeds | exceeds |
>
> **Corrected sizing on the login node: P<=4 for the gate, P<=3 for the
> merge-side validations.** The pre-registered expectation was P<=4 for both;
> **the merge-side number came in above the 400–460 MB band at 570.8 MiB, so
> P=4 fails there.** **Preferred remedy: run the pool on a batch node**, where
> the cap is 128 GiB and neither constraint binds.

#### The memory cap is host-dependent — check the right one

| Host | Cap | Established by |
|---|---|---|
| **login node** | **2.00 GiB** | the `ValidatePairBlockClosure` OOM — a real kernel kill, `constraint=CONSTRAINT_MEMCG`, `anon-rss:1996592kB`, and the reason the leak was fixed |
| **`stbc-i3`** (batch) | **128 GiB** | `user-11484.slice` `memory.max = 137438953472`, measured 2026-08-05 |

**Compare any measured peak against 2097152 kB unless the run is known to be
on a batch node.** Running the merge or the closure from the login node is the
natural thing to do and earlier sessions did it. The 437 MB above was measured
on `stbc-i3` and therefore says nothing about whether the same run survives on
the login node — at 4.8x headroom it currently would, but that margin is
against a cap 64 times smaller than the one it ran under.

**This is not a `390`-style phantom.** The 2.00 GiB figure was measured; it was
simply never attributed to a host, which is what made it look invented. An
earlier draft of this entry recorded it as non-existent. That was wrong.

#### The other ceiling: 32 hours of CPU per process

`ulimit -t = 115200`. Wall clock says how long you wait; **CPU time says
whether the process is permitted to finish at all**, and it is per process, so
a single-process merge that projects past it cannot be rescued by waiting
longer. `MEASUREMENTS.txt` extrapolates measured CPU to 3000 files and reports
the ratio. **If it exceeds 1.0, B10 is not a convenience — the merge must be
decomposed before full production can complete.**

**Interim measurement, the gate stage only** (taken live from `/proc` at
t = 3269 s, validator PID 792604, 300 files):

> **SUPERSEDED 2026-08-08 — THIS IS THE ORIGIN OF THE 0.050 ERROR, and the line
> above names the cause.** "validator PID 792604" is the **Python parent
> only**. The gate spawns a ROOT child per directory
> (`tools/validate_analysis_outputs.py:506`), and reading one PID's `/proc`
> counts none of their CPU. The measured whole-tree figure is **CPU/wall
> 0.919** (`user 3612.88 + sys 205.17 = 3818.05 s` against `wall 4156.96 s`).
> **The `rchar`/`read_bytes`/RSS rows are still valid for that process** — they
> just describe the orchestrator, not the work.
>
> **The lesson, since it is now the fifth instance:** a single-PID `/proc` read
> is not a measurement of a process *tree*. Sample the tree, or use
> `/usr/bin/time` on the top process and say which you did.

| | |
|---|---|
| CPU time | 165 s |
| wall | 3269 s |
| **CPU/wall** | **0.050** |
| `rchar` | 41.2 GB, advancing ~57.8 MB per 10 s |
| `read_bytes` | 4.74 GB — most reads served from page cache |
| RSS | 18.4 MB |

**The gate is not the CPU-ceiling risk.** At 5 % CPU utilisation, scaling
linearly to 3000 files puts the gate on the order of 2000 s of CPU against a
115200 s limit — two orders of magnitude clear. **The ceiling question
therefore belongs to the ROOT merge stage, not the checksum gate**, and only
`MEASUREMENTS.txt` can answer it because `/usr/bin/time -v` reports the whole
process tree.

Note the RSS here (18.4 MB) is far below the 437 MB the 2-second sampler
recorded earlier, which means **that 437 MB was not this validator** — the
sampler records the top three processes of the whole user, not the merge's.
Treat the sampled figures as an upper bound on *something the user was
running*, and the kernel figure from `/usr/bin/time -v` as the merge's own.

### B14. No systematic uncertainty is computed or propagated anywhere — SUBMISSION-BLOCKING, owner-action

**Not production-blocking. It does not gate `submit-full`; it gates the
manuscript.** Recorded 2026-08-09.

**The state, verified:** `Validation/MeasureUnresolvedSystematic.C` **exists**
(4300 B). **No recorded run, no artifact, no `ValidationReports` entry** — its
only mentions across `*.md`/`*.json`/`*.txt` are prose. **No systematic
uncertainty is computed or applied anywhere in the analysis.** PDF and scale
variation are not addressed either.

`REPRODUCIBILITY.md` §5 previously read "The `kUnresolved` systematic is
measured", which asserted a result from the existence of a macro; corrected
2026-08-09 (`addcb4a`) to agree with `docs/NIKHEF_BRINGUP.md` — *"No systematic
uncertainties are computed anywhere."*

**Interaction with F1.** If F1 lands OFF, scale and PDF systematics are
**argued, not computed**, in the referee response. That is a defensible position
for a tune-contrast paper and an indefensible one to discover at referee stage.
**The two decisions must be signed together.**

**Owner-action, B1-style:** what the manuscript claims about uncertainties must
match what the pipeline computes, which is currently nothing beyond the
ten-block SEM.

### B15. Four manuscript findings, and the review that prompted them is gone — SUBMISSION-BLOCKING, owner-action

**Not production-blocking, and CLOSED as a blocker 2026-08-20.** The physics
review that prompted this entry is **unavailable** — owner ruling, and a search
of the Projects tree found no such document. A blocker cannot wait on a source
that does not exist, so B15 no longer waits on one.

**What B15 reduces to is its four independently recorded findings**, listed
below. Each was measured in this repository, each cites its own evidence, and
none depends on the review. They stay open as owner-action on the manuscript,
in the same class as B1.

**Known manuscript-side items already recorded elsewhere in this file:** B1 (the
methods section describes a different study), B5 (tune-difference counts, both
wrong as measured), B8 (which tree the reproducibility statement resolves to),
and the Σ_b naming requirement — **whatever the paper calls "Σ_b" must read
`Σ_b^±`**, because Σ_b⁰ is excluded from central results.

### B13. The closure validator deletes its diagnostic log exactly when it fails

**`Validation/validate_pair_block_closure.sh` runs `rm -f "${log_file}"` on the
failure path, immediately before `exit 1`.** A genuine closure failure at full
production therefore yields **`exit 1` and nothing to read.**

**This is why B12 presented as an opaque exit code.** The merge exited 7, the
closure arithmetic had passed, and the line that would have shown the one
mismatched field had already been deleted. Reconstructing it cost a session.

**Fix: delete the failure-path `rm -f` only.** One line. **No behaviour change
on the success path** — that `rm -f` stays, and the log is still cleaned up when
there is nothing to diagnose. **It weakens no check**: the validator's verdict
is unchanged, only its evidence survives.

**Why this is a blocker and not `POST_SUBMISSION.md`:** full production is the
first run at 1000 inputs per tune, the closure is the last gate before the data
is usable, and a failure there with no log is a session lost at the worst
possible moment. The cost of the fix is one line; the cost of not having it has
already been paid once.

**Scheduled for the sync step**, with B2, B9 and the guard demotion.

**This is the fourth site of the retain-your-outputs rule** — after
`scaling_series.sh` v1 (failure path) and v2 (success path), and the same
harness deleting the 25/50-input merges a second time. **It is the first inside
a validator rather than a diagnostic harness**, which is why the rule is now
stated as covering both.

---

### B12. The closure gate rejects a correct result on a stale hardcoded count

**The merge exited 7. The closure arithmetic passed. These are not the same
thing, and the difference is one literal.**

`Validation/validate_pair_block_closure.sh:41` pins an **exact** expected
summary line and requires `grep -Fxc ... -eq 1`:

```
... object_content_sumw2_closure_checks=1500 ...
```

The run produced **1800**. Every other field in that ~200-character string
matches character-for-character.

**1800 is the correct value and 1500 is the stale one.** `ValidatePairBlockClosure.C:266-272`
says so in its own words: `sparseObjects` "omitted `hFlavourClosure`, which
7cf9f86 added to every pair file, **so the ten-block closure silently skipped
it**". Commit `b01536b` fixed that by sourcing the object list from the
generated contract — taking the count from 5 objects x 300 files = 1500 to
**6 x 300 = 1800**. `git show --stat b01536b` confirms it touched
`ValidatePairBlockClosure.C` and **not** the wrapper; the `1500` literal dates
from `5140f81` and has never been updated.

**So the gate now rejects a strictly more complete validation than the one it
was written against.** It is the B9 defect class exactly — a literal that must
move in lockstep with what it validates, in a file the fixing commit did not
open. It is the only literal of this shape in `Validation/*.sh` or `tools/`.

**Consequence, and it is not small.** The gate is the last stage of
`merge_root_files.sh`. Any campaign reaching it fails at `exit 7` **after** the
full merge has run — 6 h 44 m here, and projected far worse at production scale.
The merged data is unaffected and correct: all 33 directories promoted, each
past `validate_pair_directory.sh` and `merged_pair_provenance.py validate`
before promotion.

**Fix:** derive the expected count rather than pinning it — the wrapper can ask
the same generated contract the macro uses — or, minimally, match on
`errors=0` and the invariant fields and stop pinning a count that is a function
of the contract. **Do not simply bump 1500 to 1800**; that reproduces the defect
one contract change later.

**Partial run.** MONASH's closure ran and passed. JUNCTIONS and CLOSEPACKING
**never ran** — `exit 7` fires inside the per-tune loop on the first failure, so
their closures remain untested.

### B11. `ORDINAL ?= 1` makes the next command silently reuse a used ordinal

**Promoted to a blocker by owner decision, 2026-08-05.** I first filed this to
`POST_SUBMISSION.md` as hygiene; that was the wrong call and the owner
overrode it.

`Makefile:30` sets `ORDINAL ?= 1`. **`make submit-full` without an explicit
`ORDINAL` stamps all 3000 production jobs with ordinal 1.** This is B9's exact
defect class — a campaign parameter defaulting to a literal instead of being
derived or demanded — on the command that is next to be run, at 3000x the
scale, and with no registry to catch it because none exists.

**Measured on disk, `hadronization_production/`, 2026-08-05:**

| Campaign | ordinal | sidecars |
|---|---|---|
| HF_PT2 | **1** | 30 |
| HF_PT2_INT | 2 | 300 |
| HF_SMOKE2 | **1** | 30 |
| PTHAT2 | **1** | 1 |
| HF_SMOKE | — | no `attempt_metadata` |

**Ordinal 1 is already shared by three campaigns.** Full production would be
the fourth. The next unused value is **3**.

**This also means the Phase 4 checklist item "campaign registered with ordinal"
cannot be satisfied by a default.** It has to be an explicit, verified value.

#### Two approaches, and the design decision hiding under the better one

**A. `submit-full` refuses when `ORDINAL` is not set explicitly.** Cheapest —
drop the `?= 1` default and fail with a named remedy when it is empty. No
policy change, and it closes the silent-default hole completely. Note `ORDINAL`
is shared with `submit-smoke` and `submit-prelim`, so removing the default
touches all three; each needs an explicit value or its own.

**B. Derive the used ordinals from the campaigns on disk and refuse to reuse
one.** The derivation-not-parameterisation shape of the B9 fix, and
`campaign_ordinal_on_disk()` already exists to build on. **But it runs
immediately into a question this list cannot answer by itself:**

> **Three campaigns already share ordinal 1. Is that a defect or is it fine?**

If the invariant is *globally unique per campaign*, the existing tree already
violates it and B is not a fix but a migration. If the invariant is *unique
among campaigns that can land in one merge* — which is the property B9 actually
protected, since a merge never spans campaigns — then the existing state is
fine and B is enforcing something stricter than the design requires.

**B also cannot see the whole history:** `HF_SMOKE` has no `attempt_metadata`,
so disk derivation would report its ordinal as unused and could hand it out
again. A derivation that is silently incomplete is worse than an explicit
demand.

#### RESOLVED — Option A, owner decision 2026-08-05

**`ORDINAL` has no default and all three submit targets refuse without it.**
`Makefile` `require-ordinal` fails closed and names the ordinals already in use.
Applied to `submit-smoke` and `submit-prelim` as well as `submit-full`: all
three stamp the ordinal into event IDs, and a default that is correct for none
of them is what produced the collision.

Verified:

```
$ make submit-full
ERROR: ORDINAL is not set, and there is deliberately no default.
  Already in use: 1 (HF_PT2, HF_SMOKE2, PTHAT2), 2 (HF_PT2_INT).
  HF_RUN3_V1 is ordinal 3.
  Re-run as: make submit-full ORDINAL=3
make: *** [require-ordinal] Error 1
```

**`HF_RUN3_V1` is ordinal 3.** The invariant B was going to enforce is now
written down in `docs/DESIGN_AND_RATIONALE.md` section 3.14 rather than left as
a shared assumption: **unique among campaigns that could share a merge**, which
makes the historical reuse of ordinal 1 harmless rather than a migration
backlog. B is closed, not deferred.

#### The 30-file baseline, reconstructed rather than asserted

The previously circulated ">600 s for ~2.9 GB" was never verified by anyone.
It could not be recovered directly — HF_PT2's merge was not instrumented
either — but the promotion mtimes of its output reconstruct the run
(2026-08-03, all times +0200):

| Phase | Interval | Duration |
|---|---|---|
| validator report written | 22:48:31 | — |
| merge phase, 33 directories promoted | 22:48:31 → 23:24:52 | **36 m 21 s** |
| closure phase, 3 tunes | 23:24:52 → 23:50:16 | **25 m 24 s** |
| **total** | | **61 m 45 s** |

Internally consistent per tune: central merge ~4 min, then 10 blocks at ~60 s
each ≈ 12 min per tune, times three ≈ 36 min.

**Two corrections follow.** The circulated "~40 min at 30" is the *merge phase
only* and omits the 25-minute closure, so the real baseline is ~62 min, not
~40. And the mtimes date the validator's *completion*, not its start, so they
still do not bound the checksum gate — that is what the run above supplies.
**A two-point extrapolation is only quotable once both points come from the
same measured quantity;** do not mix the reconstructed merge wall-clock with
the instrumented gate duration.

---

## Session v6 desk work — C10 is far smaller than reported, and I was wrong

### C10 inventory — 10 figure slots, and only 2 are real work

**This corrects my own earlier claim** that "no `run_paper_plots.sh` target
produces those canvases at all". That was wrong for 8 of the 10 slots. The
evidence I missed: `improvedPlotting_THnSparse.C:1268-1270` writes
`<writeName>_PDF.pdf` / `_PNG.png` / `_MACRO.C`, and **every paper figure
except two carries exactly that `_PDF` suffix**. The live config
(`configuration_multiplicity_reduced_JUNCTIONS_THnSparse_complete_root.json`)
declares two writing global canvases — `global_balancing_plots` and
`global_balancing_baryon_over_meson_ratio`, both `write=True` — assembled from
16 mini canvases covering all three tunes, both flavours, and the
baryon/meson ratios.

| # | Slot | Live chain | Verdict |
|---|---|---|---|
| 1 | `Model.tex:130` `MultiplicitySpectrum_Shared_shape.png` | macro emits `MultiplicitySpectrum_Shared_` | **FILLS** |
| 2 | `Results.tex:48` `CharmCorrelations_MONASH_PDF.pdf` | `cCharmCorrelations` canvas | LAYOUT |
| 3 | `Results.tex:71` `BeautyCorrelations_MONASH_PDF.pdf` | `cBeautyCorrelations` canvas | LAYOUT |
| 4 | `Results.tex:92` `global_balancing_plots_integrated_charm_PDF.pdf` | `global_balancing_plots` | LAYOUT |
| 5 | `Results.tex:105` `..._multiplicity_charm_PDF.pdf` | same canvas | LAYOUT |
| 6 | `Results.tex:126` `..._integrated_beauty_PDF.pdf` | same canvas | LAYOUT |
| 7 | `Results.tex:139` `..._multiplicity_beauty_PDF.pdf` | same canvas | LAYOUT |
| 8 | `Results.tex:152` `global_balancing_baryon_over_meson_ratio_multiplicity_PDF.pdf` | `global_balancing_baryon_over_meson_ratio` | **FILLS** |
| 9 | `Results.tex:170` `globalCanvasYieldsPDF_215.pdf` | none — thesis-era naming | **NOTHING** |
| 10 | `Results.tex:182` `globalCanvasRelativeYieldsPDF_215.pdf` | none — thesis-era naming | **NOTHING** |

**FINAL COUNTS: 2 fill directly, 6 need `writePath` set or a layout split,
0 need writing.**

**The 2 "nothing fills" rows resolve to zero work — confirmed by reading the
document structure, not inferred.** `Results.tex:157` closes the `\enumerate`
that holds slots 1-8. `:159` then opens

> `\textbf{UNDER CONSTRUCTION -- placeholder text from thesis} \\`

and everything after it to end-of-file (`:185`) is inside that block: two
`\subsection`s of thesis prose plus the two `_215` figures, which are cited *by*
that prose (`Fig.~\ref{fig:secResults:GlobalYieldsBBCC}` at `:162`,
`Fig.~\ref{fig:secResults:GlobalRelYieldsBBCC}` at `:176`). **They are deleted
with the block they belong to, not regenerated.**

**So C10 requires no new producing target and no new code.** My earlier claim
that "no `run_paper_plots.sh` target produces those canvases at all" was wrong
twice over: wrong for the 8 live-chain slots, and wrong to treat the remaining 2
as work.

The 6 LAYOUT rows are one canvas the paper wants split four ways
(charm/beauty x integrated/multiplicity) plus two correlation canvases that
exist but whose write path is not configured (`writePath=None`, and
`:2463-2467` only writes when `write && writePath && writePath != "NONE"`).
**That is configuration, not new code.**

**And the 2 NOTHING rows are probably zero work**: both sit inside the block
`Results.tex:159` marks `\textbf{UNDER CONSTRUCTION -- placeholder text from
thesis}`. They are the thesis figures the placeholder prose refers to, and
will most likely be deleted rather than regenerated when that prose is
replaced. **Confirm with the owner before treating them as work.**

*Naming conventions distinguish the two families cleanly:* `<name>_PDF.pdf` is
the live macro; `globalCanvas*PDF_215.pdf` and `PDF_*_215.pdf` are thesis-era.
**Figure mtimes are useless for provenance** — all 10 read `2026-07-27 16:24`,
a bulk copy.

### C9 — the observables exist; the prose does not match them

The live config emits mini canvases for **all three tunes** and both flavours,
including `baryon_over_meson_ratio` variants. So the observables
`Results.tex:162-166` asserts are within the live chain's scope. **C9 is not
missing machinery — it is prose written against thesis-era output.** It needs
rewriting against regenerated figures, not new code. Whether the Sigma_b claims
survive is the statistics question (section 3, Sigma_b at 10 % scale).

#### The statistics question, answered by sampling rather than summation

**C9 is reachable before full production.** Measured 2026-08-05 by opening
**one** per-job pair file per tune (`slot_000`, 100k events) and reading
`hCorrelations` entries — deliberately not a summation, so it cannot disagree
with the merged numbers when they land:

| Pair | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `BplusSigmabzero` | **4** | **57** | **36** |
| `BzeroSigmabzero` | **2** | **74** | **30** |
| `BplusLb` | 29 | 46 | 42 |
| `BzeroLb` | 33 | 32 | 26 |
| `BplusBminus` *(control)* | 159 | 84 | 99 |

**Sigma_b is populated, and the tune ordering the prose asserts is already
visible in a single job.** JUNCTIONS carries 14-37x MONASH's Sigma_b while
Lambda_b is comparable across tunes (26-46) and the common-species control stays
within a factor of two — so the effect is in the Sigma_b/Lambda_b ratio, not in
an overall normalisation difference.

**At 10 % scale (100 jobs/tune) this projects to** ~400 MONASH and ~5700
JUNCTIONS `BplusSigmabzero` entries. The limiting arm is MONASH Sigma_b at
~5 % statistical precision, against an effect of order 14x. **Adequate.**

*Caveats, since this is one job:* the per-tune numbers carry Poisson noise of
order sqrt(N), so MONASH's 4 is really "a few"; the projection is
order-of-magnitude, not a measurement. The `...bar` variants read 0 throughout,
which is the `ordered_conditional_v1` pair convention rather than missing data.
**Confirm against the merged output when it lands** — this sampling exists to
unblock the scoping decision, not to replace the authoritative numbers.

#### Does the paper attribute the enhancement to the right cause? Yes — and CLOSEPACKING proves it

**The concern raised was that `Results.tex` might credit the Sigma_b
enhancement to `StringFlav:probQQ1toQQ0join`, whose direction is wrong for it.
It does not.** Read directly, the causal claim is CR, not the diquark
parameter:

> "This is explained by the fact that the `uu` and `dd` di-quarks are necessary
> to create the Sigma_b^{+/-} baryons and can only exist in a isospin-1 state,
> while the Sigma_b^0 baryon contains a `ud` di-quark that can reside in the
> much more energetically favoured isospin-0 state. **This suppression is lifted
> when CR mechanisms are at play as they allow hadronisation without spin
> dependence.**"

The parameter appears later and is used for something else entirely — the
*beauty-versus-charm* asymmetry — and the paper's narrow claim about it is
**correct**: "The parameter has identical values in the Junctions tune" means
identical *across flavours within* JUNCTIONS (0.0275 four times, so no
charm/beauty split), not identical to MONASH.

**The card values, verified directly:**

| Tune | `probQQ1toQQ0join` | `ColourReconnection:mode` |
|---|---|---|
| MONASH | **not set** — inherits `Tune:pp = 14` | not set |
| JUNCTIONS | **0.0275, 0.0275, 0.0275, 0.0275** | **1**, `allowJunctions = on` |
| CLOSEPACKING | **0.5, 0.7, 0.9, 1.0** | **1**, `allowJunctions = on` |

**CLOSEPACKING is the control that settles it.** It carries the *same* diquark
parameter values the paper states as the Monash default, and MONASH leaves the
parameter unset — yet CLOSEPACKING shows ~9x MONASH's Sigma_b (36 vs 4). The
variable that tracks the enhancement is `ColourReconnection:mode = 1` with
`allowJunctions = on`, present in both enhanced tunes and absent in MONASH.
**The parameter cannot be driving it, and the tune that isolates the two
variables is already in the campaign.**

**Where the paper is nonetheless exposed.** It never mentions that JUNCTIONS
*lowers* `probQQ1toQQ0join` by roughly thirty-fold. A referee who reads the
cards will find a 30x suppression of exactly the spin-1 diquark channel that
makes Sigma_b, and will ask why the yield rises anyway. **The answer strengthens
the paper rather than weakening it** — the enhancement survives a 30x
suppression of the diquark route, which is strong evidence the junction channel
dominates and is spin-blind, exactly as the prose claims — **but it is currently
unstated, and an unstated answer reads as an oversight.**

**Report only, per owner instruction. No paper edit proposed.** Confirm the
ratios against merged statistics before any of this is written down as physics.

#### The arms are nested in junction CR — but no pair isolates one mechanism

**The nesting is real.** MONASH sets no `ColourReconnection` key at all
(inherits `Tune:pp = 14`, i.e. MPI-based CR, *not* junction CR); JUNCTIONS and
CLOSEPACKING both set `ColourReconnection:mode = 1` with
`allowJunctions = on`. So the three arms are *no junction CR* → *junction CR* →
*junction CR + close packing*, and MONASH is not a third parallel mechanism.

**But "JUNCTIONS and CLOSEPACKING share their CR configuration entirely" is
false, and it is the load-bearing half of the claim.** Diffing the two cards,
non-comment settings only:

```
shared: 24    JUNCTIONS-only: 8    CLOSEPACKING-only: 20
```

The CR block itself is retuned between them, and so is fragmentation:

| Setting | JUNCTIONS | CLOSEPACKING |
|---|---|---|
| `ColourReconnection:m0` | 0.3 | **0.618** |
| `ColourReconnection:junctionCorrection` | 1.20 | **1.349** |
| `ColourReconnection:mPseudo` | *(unset)* | **0.403** |
| `StringFlav:probQQ1toQQ0join` | 0.0275 x4 | **0.5, 0.7, 0.9, 1.0** |
| `StringZ:aLund` / `bLund` | 0.36 / 0.56 | **0.68 / 0.98** |
| `StringFlav:probQQtoQ` | 0.078 | 0.081 |
| `StringFlav:probStoUD` | 0.2 | 0.217 |
| `MultipartonInteractions:pT0Ref` | 2.15 | 2.194 |
| `StringFragmentation:doStrangeJunctions` | *(unset)* | **on**, `enhanceStrangeJunction = 0.540` |
| `ClosePacking:*` | *(absent)* | 7 settings, incl. `baryonSup = 0.928`, `doEnhanceDiquark = off` |

**So JUNCTIONS -> CLOSEPACKING is the *most* confounded comparison available,
not the cleanest.** It moves close packing, the CR geometry, the Lund
fragmentation function and four flavour-composition parameters simultaneously.
Reading 57 -> 36 as "close packing attenuates the enhancement" is not supported:
`probQQ1toQQ0join` rises thirtyfold across that same step, and `aLund`/`bLund`
nearly double. This is the tune-bundle confound already recorded at
`DESIGN_AND_RATIONALE.md` 3.10 and `REPRODUCIBILITY.md` section 5 — it applies
to *this* pair with full force.

**The inversion worth noticing:** MONASH -> CLOSEPACKING, called the conflated
comparison, is the pair that **matches on `probQQ1toQQ0join`** (MONASH inherits
0.5/0.7/0.9/1.0; CLOSEPACKING sets exactly those). It is therefore the one
comparison that *controls* the diquark parameter while changing CR — which is
why it, not JUNCTIONS, is what makes the "CR drives Sigma_b, the diquark
parameter does not" argument above hold.

**Consequence for the decomposition.** Report all three pairwise contrasts as
asked, for the inclusive baryon fraction and for Sigma_b/Lambda_b — but label
each with what it actually varies, and **do not attribute any of them to a
single mechanism.** None of the three is a controlled experiment.

#### There is no overreach to fix — `Model.tex:60` already states the limit

**Checked directly, and the concern does not apply.** `Model.tex:60` reads:

> "These are complete configuration bundles rather than single-parameter
> variations: MONASH and JUNCTIONS differ in 13 effective settings, and MONASH
> and CLOSEPACKING in approximately 20, including the Lund fragmentation
> parameters $a$ and $b$ and the multiparton-interaction regularisation scale.
> **Differences between the configurations are therefore attributed to the full
> bundles, and not to junction formation, close packing or diquark production
> individually.**"

That is exactly the resolution limit the design supports, already written, in
the paper's own methods section. **No sentence in any `.tex` file attributes an
effect to close packing specifically**, and `grep` over all seven files returns
**zero hits for `3.68`** — consistent with section 0 of this document, which
found the same for `3.2`, `0.44` and `0.59`. **The 3.68x is an internal working
number that was never promoted into the manuscript.** There is nothing to
reword.

The remaining exposure on that line is C5/B5, unchanged: the counts "13" and
"approximately 20" are still untallied against
`Validation/AuditTuneSettings.C`. Note a raw card diff cannot settle them —
MONASH inherits most of its values from `Tune:pp = 14` rather than stating
them, so "effective settings" is not the same measure as "lines that differ".

#### Fourth arm, costed — an option, not a proposal

**Cards:** one new file, CLOSEPACKING's with `ClosePacking:doClosePacking = off`
and nothing else changed; the six other `ClosePacking:*` keys become inert but
should stay for diffability. **Tune sites:** the audit counted **at least 14**
hardcoded three-tune assumptions (`merge_root_files.sh:186,202`;
`campaign.py:34`; `validate_analysis_outputs.py:20`;
`statistical_robustness.py:39`; `generate_registry_artifacts.py:359`;
`validate_tune_cards.py:10`; four `PlottingScripts` sites; two test files) —
so **`TuneOrdinal()` is emphatically not all the code required**; the one-line
ordinal addition is the smallest part, and every hardcoded triple is a place
the fourth arm is silently dropped or trips an equal-exposure check.
`build_canonical_manifest.py:119,128` refuse unequal exposure, so the arm needs
the *same* job count as the others, not a cheap subset. **CPU:** at
CLOSEPACKING's measured 989 s/job, 1000 jobs is **275 CPU-hours**, taking the
campaign from 562.5 to **~837**, a 49 % increase; at 10 % statistics it is
~27 CPU-hours, which is the sane first step. **Schema:** the 2-bit tune field
does hold four and `JUNCTIONS_MATCHED` is ruled out of production, so this
fits without the widening already rejected — that part of the premise is
correct. **Verdict:** cheap in physics, moderate in CPU, and the real cost is
the 14 sites. A referee-response option, not a first-submission one.

### B4 reuse — `freezeMultiplicityBoundaries_THnSparse` cannot be reused

**One line, as asked:** it computes no percentiles — it *seals* an
already-frozen receipt from the config and throws
`"Multiplicity-boundary receipt was not frozen"` if one is absent
(`improvedPlotting_THnSparse.C:1276-1282`).

The real percentile logic is in
`Plot_MultiplicityDistribution_PercentileBoundaries.C`, and it consumes a
**`TH1D`** multiplicity histogram (`:519`) read from `complete_root`
(`:272-273`). **The A2 path produces no histogram at all** — it accumulates
scalar counters and prints means
(`CalibrateMultiplicityAgainstMinBias.C:106-149`).

**So the minimal thing to build is: have the A2 macro fill and write a `TH1D`
of `N_ch` per arm** (hard and MB, per tune) on a common binning. Then the
deliverable is a cumulative-integral evaluation — for each hard-sample
percentile boundary in `N_ch`, its percentile in that tune's MB `TH1D`. Note
this is the *inverse* of what the existing macro does (it maps percentile ->
boundary; B4 needs boundary -> percentile), so the arithmetic is new either
way, but it is a few lines rather than a new code path to validate.

### Discard bias — the mechanism is clean; "unbiased" needs one more assumption

**Mechanism, verified in `runCondorJob.sh`:** the producer writes to
`partial/<TUNE>/<stem>.partial.root` (`:190`). Promotion to `raw/` happens only
after the producer exits 0 (`:276-279`), wrote a file (`:280-283`), and the
validator passed (`:358`) — via `mv -n` (`:367`, no-clobber) with a post-move
SHA re-check (`:369`). **A guard kill therefore promotes nothing.**

**Observed:** all 8 killed jobs left orphans, retained and unpromoted, at
**21.9-88.7 MB against ~96 MB for a complete file** — genuinely truncated, 23-92 %
through. Promoted counts stayed 100/95/97, so no truncated data entered the
sample.

**Retry seeds are independent of what was discarded:** `seed_for(tune, job,
attempt)` (`campaign.py:97`) depends only on those three values;
`resubmit_held.py` selects slots by *absence of promoted output* and never
inspects discarded content.

**The honest caveat, which the easy answer misses.** Whole-job discard plus an
independent redraw means no partial data is mixed in — but the retained sample
is still conditioned on *"jobs that completed"*. If hang probability correlates
with the event content of a job, completed jobs under-represent whatever causes
hangs. That matters here specifically because **every hang so far has been a
colour-reconnection tune**, and dense-junction events are both the plausible
hang candidate and the events the paper's baryon observables measure.

#### The bound, computed — a stated limitation the paper can use

A caveat is not publishable; a bound is. Worst case, assume the hang *is*
content-driven: a class of event E exists such that any job containing one
hangs and is discarded. Then E-events can **never** appear in the retained
sample, and the bound follows from the measured hang rate.

- measured: **8 hangs / 300 jobs = 2.67 %** of jobs contain >=1 E-event
- Poisson: `1 - exp(-lambda) = 0.0267` -> **lambda = 0.0270 E-events per job**
- per event: `0.0270 / 100,000` = **2.7 x 10^-7**
- over the campaign: `0.0270 x 300` = **~8.1 E-events absent from 3 x 10^7**

**Bound: the retained sample is missing at most ~8 events in 3 x 10^7, a
fraction of 2.7 x 10^-7.** Worst case for any observable is all 8 landing in one
bin, so the relative bias on a bin holding `N` entries is `<= 8/N`:

| Observable scale | entries | max relative bias |
|---|---|---|
| Lambda_b yield, multiplicity-integrated (~66k at 3x10^7) | 6.6 x 10^4 | **1.2 x 10^-4** |
| a rare species in one multiplicity class | ~10^3 | **~0.8 %** |

**Sentence the paper can use:** *"Jobs terminated by the generator hang guard
are discarded whole and regenerated with independent seeds, so no truncated
output enters the sample. Because the retained sample is nonetheless
conditioned on job completion, a hypothetical event class that always induces a
hang would be absent from it; the measured hang rate of 2.7 % of jobs bounds
this at ~8 events in 3 x 10^7 (2.7 x 10^-7), i.e. below 10^-4 relative on any
multiplicity-integrated heavy-flavour yield."*

**Assumption it rests on**, stated so a referee can weigh it: at most one
pathological event per hung job. If a hang instead reflected a job-level
property the bound would not apply — but jobs differ only by seed, so there is
no job-level property other than the random sequence. **Scale the numbers with
the measured hang rate for the full campaign; do not carry 2.7 % forward
unchecked.**

---

## Cleared this session

| Was | Now |
|---|---|
| Seed ledger 121 -> 122 unexplained; a seed-consuming path might not record | **Closed.** Line 122 = `101500003` = JUNCTIONS job 2 attempt 5, burned by `submit_HF_PT2_retry5.sub` at `2026-08-03 13:53:06`, ten hours *before* v3 was committed (`aa831f1`, 23:51:29). v3's 121 was a mid-session count. No unlogged path exists |
| Producer provenance across this session's edits | **Closed.** Forced rebuild at `e690e17` reproduces `e54b27bb...` byte-for-byte (`PRODUCER_BUILD_READY ... forced_rebuild=true`). Nothing in the translation unit moved |
| A2 method trusted but not re-verified | **Closed.** All five scan points reproduce bit-exactly (6.968 / 4.613 / 4.973 / 6.678 / 10.492), cluster 5319322, all `A2_EXIT=0` |
| Which macros are live vs predecessor, and what they read | **Closed.** See `POST_SUBMISSION.md` section "Chain map" |
