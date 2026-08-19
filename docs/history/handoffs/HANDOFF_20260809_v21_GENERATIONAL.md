# Handoff v21 — GENERATIONAL. Written for a successor who has read nothing

**You are inheriting a live production campaign and a half-finished analysis
change. This document assumes you have the repository and nothing else.** Read
it before touching anything. Where it says a thing is inviolable, it is because
breaking it costs days.

| | |
|---|---|
| **Local HEAD at time of writing** | **`3ae63f1`** on `physics-focus` |
| **Nikhef HEAD** | **`e6429b7`** — behind local, deliberately, see §1 |
| **Cluster** | **`5390385`**, HF_RUN3_V1, campaign ordinal **3** |
| **Campaign** | **1545 / 3000 = 51.5 %** complete |
| **Seed ledger** | **3430 lines, 3430 unique** |
| **Held** | **1** (genuine hang guard, §3) |

---

## 0. Where you are, in one paragraph

This is a PYTHIA study of heavy-flavour hadronisation: three tunes (MONASH,
JUNCTIONS, CLOSEPACKING) differing in colour reconnection and fragmentation,
compared through **b/c-hadron pair correlations at fixed event activity**. Full
production is **running right now**. The analysis that will consume it has a
known, agreed gap — 33–49 % of compensating heavy flavour is invisible to the
current species accounting — and the fix is designed, authorized, and waiting
for you to implement it.

**The working directory is `Hadronization-physics-focus`, NOT `Hadronization`.**
The sibling is `main` at `11884cf` and contains none of this infrastructure —
no `Makefile`, no `tools/`, no `docs/`. **If those look missing, you are in the
wrong directory.** They share one git object store (`docs/WORKSPACE.md`).

---

## 1. THE CHECKOUT FREEZE — inviolable until the campaign completes

> **The Nikhef checkout at `/data/alice/ipardoza/Hadronization` stays at
> `e6429b7`. Do not move it. Do not sync. Do not `git pull` there.**

**Why:** every job verifies its commit at startup. **1455 jobs have not started
yet.** Advancing the checkout fails every one of them.

**Local commits accumulate freely** — that is the intended pattern, and the gap
between local `3ae63f1` and Nikhef `e6429b7` is correct, not drift.

**If something must run on Nikhef with new code, use the scratch-deploy
pattern:** copy to `/data/alice/ipardoza/<name>/`, record the deployed file's
**sha256 and source commit** in a `run_meta.txt`, and invoke the deployed copy
**explicitly** — never `$PROJECT`'s, which is the frozen version. Worked
examples: `/data/alice/ipardoza/b4_mapping/` (with its
`SimulationScripts` symlink, because the macro has a relative include that a
flat copy breaks).

**The freeze ends** when the campaign completes → §7.

---

## 2. Connecting, and two traps that have each cost a session

```bash
ssh -o BatchMode=yes -o RemoteCommand=none -o RequestTTY=no stbc '<cmd>'
```

- **`-o RemoteCommand=none -o RequestTTY=no` is mandatory.** Without it you get
  `Cannot execute command-line and remote command` and nothing else.
- **ROOT needs a login shell**: `bash -lc "…"` or `ssh stbc 'bash -l -s' <<'EOF'`.
  The heredoc form avoids nested-quoting misery.
- **An `ssh` that launches a detached job hangs until its timeout.** The job
  survives. **Check the PID; do not relaunch.**

---

## 3. THE LIVE CAMPAIGN — your standing duty

**HF_RUN3_V1**, cluster `5390385`, 3000 jobs (1000 per tune × 100k events),
submitted 2026-08-09T04:17:14Z, **released 04:23:55Z**. Full record:
`docs/campaigns/HF_RUN3_V1_RECORD.md`.

| tune | promoted | note |
|---|---|---|
| MONASH | **1000 / 1000** | block complete, **zero hang holds** |
| JUNCTIONS | 543 | running |
| CLOSEPACKING | 0 | jobs 2000+, not started |

**Monitoring — read REASONS, never counts:**

```bash
condor_q 5390385 -af JobStatus | sort | uniq -c
condor_q 5390385 -constraint 'JobStatus==5' -af HoldReason | sort | uniq -c
```

### The two hold classes — identical in a summary line, opposite in meaning

| hold | when | means | do |
|---|---|---|---|
| `HoldReasonCode 15` "at user's request" | at submit, **all** jobs | the **parking brake** — jobs are submitted held by design (`render_production_submit.py:286`) | **release** |
| `HF_HANG_GUARD suspected generator hang` | after **>3600 s CPU** or **>14400 s wall** | a wedged generator | **retry** |

**"N held" is evidence of nothing until you read the reason.** Full table in
`docs/PHASE4_SUBMISSION_CHECKLIST.md` §B3 and `Condor_README.md`.
**This campaign is already released**, so any new hold is the second kind.

### THE ONE HELD JOB — your first retry

`5390385.1003` = **JUNCTIONS logical_id 3**, `RemoteUserCpu 3607.0 s`,
wall 3616.0 s, **CPU/wall 0.9975**, `NumJobStarts 1`.

**Genuine hang**: CPU just past the 3600 s guard, and CPU/wall ≈ 1 is the
wedged-generator signature — a hung generator burns CPU at ~97 %+, a
slow-but-healthy job on a contended node shows a low ratio
(`Makefile:38-40`).

**Left held deliberately.** `tools/resubmit_held.py` has **never run on more
than one job**. A batch of one is the gentlest possible first exercise of it.
**Verify the reason and CPU yourself before retrying**, then run it per its
normal flow from the frozen checkout — it carries B9's ordinal derivation and
B15's v2 seeds. **Record: jobs retried, ledger line count before/after, attempt
indices.** If it misbehaves on a batch, **STOP and retain everything.**

**LOUD FLAG:** *any* **MONASH** hang-guard hold would be **the first in project
history** — zero across three campaigns and all 1000 jobs of this one. **Do not
fold it into routine retries. Report it prominently.**

**Budget:** ~2.7 % hang rate, two-to-three retry rounds, `MAX_ATTEMPTS = 10`
(`campaign.py`). Current rate 1/1545 = 0.06 %, but **the CR tunes carry
essentially the whole hang history** (means 659 s and 989 s vs MONASH's 377 s)
and have only just begun.

### Outstanding: the last seed verification

**`seed_derivation_v2` is live-verified for MONASH (`130000001`) and JUNCTIONS
(`131000001`).** **CLOSEPACKING must show `132000001`** — jobs 2000+, not
started. **That is the only unverified factor of the seed formula.** Check the
first `PRODUCTION_START` line in
`hadronization_production/HF_RUN3_V1/condor_logs/CLOSEPACKING/*.out`.

---

## 4. YOUR FIRST SESSION — an ordered queue

### (1) The scoped `config/` authorization — GRANTED, execute it

> **Owner ruling, verbatim: the scoped `config/` authorization is GRANTED. Add
> `hFlavourClosureSpecies` to `config/pair_file_object_contract_v1.json` and
> regenerate via `tools/generate_registry_artifacts.py`.**

**Why it is needed:** `Validation/ValidatePairDirectory.C:384` fails a directory
on `"unexpected object …"`. The contract is
`AnalysisScripts/GeneratedPairObjectContract.h`, marked
`// GENERATED FILE -- DO NOT EDIT`, generated from that JSON. **Any new object
in a pair file needs the contract to know about it.**

> **REQUIREMENT ATTACHED — do not skip this.** The contract is **exact-match in
> both directions**. A regenerated contract expecting seven objects **must not
> fail existing v2 directories that correctly carry six.** The work must be
> **version-aware** — selection by the output's schema tag, or explicit v2/v3
> contract coexistence — **failing closed on mismatch.**
>
> **This is defect pattern 2: a contract change taught to one consumer and not
> its siblings.** Design the answer *before* the edit. **In the same pass,
> check the five sibling literals in `validate_pair_block_closure.sh:67` for
> object-count sensitivity** (`POST_SUBMISSION.md` has them).

### (2) The species axis — implementation and validation are ONE item

**Ratified design:** `hFlavourClosureSpecies` as a **new** object;
**`hFlavourClosure` stays byte-identical.**

> **Owner ruling, verbatim: the parallel-object design is ratified — the
> 49×-cliff risk pricing is accepted: an unattributable cost cannot be
> extrapolated, and the merge's cost profile does not change under a live
> campaign.**

*(Background: `hFlavourClosure` carried 124,494 filled bins at 100 inputs and is
the object whose merge cost produced a 49× step whose mechanism is **unknown** —
chunking was falsified. Widening it in place could not be bounded.)*

**Four sites**, in `AnalysisScripts/status_analysis_THnSparse_qq.C`:

| site | what |
|---|---|
| `MakeClosure:623` | clone the shape; **species ordinal replaces the category axis** |
| fill `:1008` | fill the new object beside `hFlavourClosure` |
| write `:1122` | write it, plus the label object |
| init | load the ordinal table |

Plus: **ordinal-table loading** from the ratified artifact; **fail-closed
mapping** — any sector-charged PDG outside the table **aborts with a named
error, no overflow bin**; **v3 schema tagging** per F5; and **axis legibility** —
write the ordinal→PDG map into each output file as an object, following
`status_analysis_THnSparse_qq.C:1157-1163`
(`associate_origin_category_labels`). **A reader of the file must decode the
axis without the repository.**

> **THE STANDING RULE, ratified: implementation and validation are ONE
> indivisible item. Do not commit code without its validation green.**

**Validation — end-to-end on the fixture, ROOT-only, contract env vars. Two
exact checks:**

1. **Closure sum rule still closes to 1 within 1e-9.**
2. **Species-axis totals summed by category reproduce the 6-category axis
   bin-for-bin.**

**A mismatch is a STOP with the discrepancy quantified — not patched.**

**Why check 2 is genuine and not tautological:** the species→category mapping is
derived independently (registry flag + spin type) from the producer's
`heavyStateCategory`. Summing one and comparing to the other tests **two
independent paths**.

**Everything is staged for you:**

- **Fixture:** `HF_PT2_INT/raw/JUNCTIONS/hf_JUNCTIONS_job001.root`, sha256
  `49657c2c9a25e319513be5cda659a4d5e53bb3944f33bef51702b5660aaa3651`,
  96,578,417 B, verified byte-identical. Re-`scp` it; local scratch is not
  durable.
- **Ordinal artifact + generator:** `tools/GenerateSpeciesOrdinals.C` (`bec170f`).
  **202 species, ordinals 0..201.**

### (3) Campaign duties throughout — §3.

---

## 5. THE SETTLED DECISIONS — do not re-litigate; each has a record

| decision | record |
|---|---|
| **Gate list G1** and its **shrink-only rule** ("the list only shrinks; any addition is a STOP naming the cost of delay") | `RELEASE_BLOCKERS.md` "THE PRODUCTION-GATE LIST" |
| **G2: Option A, combined production.** B_c declared **multiplicity-integrated / top-class-only**; bb̄ top-up survives post-submission | `RELEASE_BLOCKERS.md` G2; memo §5 |
| **Axis: common absolute N_ch boundaries**, one set for all tunes and both sectors, labelled as MONASH-MB percentiles: `-0.5, 2.5, 3.5, 5.5, 6.5, 8.5, 10.5, 13.5, 17.5, 23.5, 32.5` | memo §5c; `RELEASE_BLOCKERS.md` M6 |
| **F1: variation weights OFF** — the three arms *are* the hadronisation variation | `DESIGN_AND_RATIONALE.md` §3.15 |
| **B15: `seed_derivation_v2`** — the campaign ordinal is in the seed | `RELEASE_BLOCKERS.md` B15b; `REPRODUCIBILITY.md` §2 |
| **Staged registry work** (stage-1 analysis-side, stage-2 rides a future campaign) + **F3–F6** | `REGISTRY_AND_MAPPING_PROPOSAL.md` §3b |
| **F5 coexistence**, with the legibility condition | proposal §3b (F5-DRAFT) |
| **202-ordinal table**, hidden-heavy excluded | `bec170f`; §6 below |

> ### THE WARNING THAT WILL MISLEAD YOU IF YOU SKIP IT
> The axis translation table's **maximum residual is 2.91 pp**, and every class
> is inside 3 pp. **THIS IS NOT THE FAILED CRITERION PASSING.**
>
> B4's pre-registered gate asked whether **per-tune** boundaries land at the
> same MB percentile. **They do not — 5 of 11 outside ±3 pp.** That failure is
> what caused the convention to change.
>
> The 2.91 pp is a **different quantity**: how far a **common** boundary's
> meaning drifts between tunes. **It is the published residual, not a pass.**
> Both tables are in memo §5b and §5c. Quoting the second as if it were the
> first would misrepresent the result.

**Why hidden-heavy states are excluded from the 202:** J/ψ, Υ, χ carry
`q_c = q_b = 0`. They cannot compensate, so they cannot appear on a
compensation axis — including them would add 17 bins that can never fill.
219 audit rows − 17 hidden = **202**.

---

## 6. THE POST-CAMPAIGN QUEUE — when the last job promotes

1. **Sync — this ends the freeze.** Verify `condor_q` empty for `ipardoza` by
   **full output**. Bundle local commits, `git fetch` + `merge --ff-only` on
   Nikhef. Then: **`make check` bare** (expect the current count — it was 25/25
   at `e6429b7`; your contract work will change it, so **pre-register the new
   number before running**) and **producer rebuild — expect byte-identical
   `e54b27bb9e3f…`**. **If the producer SHA moves, STOP** — something touched
   the translation unit.
2. **B6 discharge.** `thnsparse` and `audit-subsamples` are
   **`PlottingScripts/run_paper_plots.sh` targets, not Makefile targets.**
   Blocked because **no `hf_pt2_int` dataset exists in either selector** —
   needs a `config/` edit *and* a synced checkout. **Verify the selector JSONs
   are not sha-pinned in any provenance chain first.**
3. **Merge at scale.** Projections: **17.7 h pessimistic / 6.2 h measured** CPU
   for the largest directory, against the **32 h per-process** ceiling —
   **it does not bind under either model** (`RELEASE_BLOCKERS.md` B10).
   **Pool sizing, measured:** gate child **440.9 MiB**, merge-side
   **570.8 MiB** ⇒ on the **2048 MiB login cap**, **P≤4 for the gate, P≤3
   merge-side**. **Prefer a batch node** (128 GiB) where neither binds.
4. **v3 analysis planning** at full scale, under the new schema.
5. **F3** (virtual-trigger closure) and **F4** (PYTHIA-linked decay-parent
   probe) — proposal §3b.
6. **Boundary wiring into the plotting config** — deferred with B6, named, not
   started.

---

## 7. WORKING PRACTICES — carried forward whole

- **Cite `path:line` or a commit SHA for every claim.** Assert something works
  only when you have run it and can quote the output line.
- **Record the method beside every number.** Its absence caused every scope
  error in §8.
- **Verify owner-supplied claims against source before acting.** A failed
  verification is a **STOP with the discrepancy reported**, not a silent
  adaptation. This has caught stale briefs repeatedly.
- **Pre-register expectations before measuring**, and report the scorecard
  whether or not they held. It is what made the wrong ones visible.
- **Prefer a bound to a measurement where a bound suffices.** `CPU ≤ wall`
  closed a check that survived a prediction being wrong by 20×.
- **STOP ends the item** — record it and continue the queue. **SESSION-STOP**
  is explicit and ends everything.
- **Retained outputs, unconditionally.** A diagnostic harness **and a
  validator** keep their outputs — especially on failure. Earned four times.
- **Report non-results as non-results.** "Not available" beats a plausible
  number.
- **Contradict the owner when the evidence says so.** The most valuable
  findings here came from exactly that, in both directions.

### Prohibitions

Never `git add -A`; never `git stash -u`; **never touch the seed ledger outside
`tools/campaign.py`**; never move the Nikhef checkout while jobs are queued;
never delete anything not explicitly approved; **never discover a cluster id
with `condor_q -af ClusterId | tail -1`**; **never `pkill` by pattern on a
shared host** — kill by recorded PID only; never submit anything from
`/data/alice/ipardoza/quarantine/`; **never run
`validate_analysis_outputs.py` with `--report`** — it rewrites a file whose
sha256 is recorded in all 33 promoted directories' provenance.

**Untouchable:** `Paper/**`, all four tune cards, `config/*.json` (except the
granted authorization in §4.1), generated headers, existing
`docs/handoffs/**` files (new ones are committed as usual), promoted data.

**No change that is not on `RELEASE_BLOCKERS.md`. Everything else goes to
`POST_SUBMISSION.md`.**

---

## 8. THE ERRORS THIS GENERATION MADE AND CAUGHT

**Read this section. The mutual-correction culture is the most valuable thing
being handed over, and it only transfers if you can see it working.** Every one
of these was caught by the other party, or by the same party checking its own
work against an independent number.

| error | how it was caught | lesson |
|---|---|---|
| **The gate recorded as latency-bound at CPU/wall 0.050** — used to justify a remedy | Standalone P=1 run measured **0.919**. The origin was in the file itself: a single-PID `/proc` read that missed the ROOT children | **A single-PID sample is not a measurement of a process tree** |
| **cc̄:bb̄ "~10:1"** in a brief | Measured **6.39:1** over 10⁶ events/tune. Origin: the C6 table's *accepted-quark* counts read as an *event* ratio | **Establish two numbers measure the same thing before comparing** |
| **`Tune:pp = 14`** — the B4 macro took a `tuneLabel` but read no card | Caught while preparing the launch, not while writing the code. Would have produced **three identical MONASH samples** agreeing at 0.0 pp and **passing** the ±3 pp gate | **An agreement gate is meaningless until a difference check passes.** That check is now institutionalised in the harvest contract |
| **`FindBin` off-by-one** on a half-integer edge | The translation table read MONASH c2 as 19.40 % against the boundary table's 11.803 % — **the same quantity**. Only having both tables exposed it | **Compute a quantity two ways when it is going into a paper** |
| **"the guard demotion"** — referenced in five handoffs with no antecedent | Refused to guess; phrase-matched it to the per-tune CPU guard in `POST_SUBMISSION.md:236` | **Do not guess at a change that touches a guard** |
| **Seed collision at render** — every campaign drew the same sequence | `assert_seeds_unused` refused it; **nothing was burned**. The audit then found the attempt axis had been used as a de-facto campaign counter, **8 of 10 slots gone** | **The guard that fires is worth more than the one that never gets tested** |
| **B4's ±3 pp gate failed** | Reported as an escalation with no convention change, per pre-registration — which produced a **better** convention than the one being tested | **A failed gate can be a result** |

**Two things the owner corrected in me, recorded because they cut the other
way:** the claim that a merge could not complete full production (two scope
errors, retracted); and the reading that "no transition by 100 inputs" was the
*safe* branch when it was the dangerous one.

---

## 9. COLD-READ SELF-REVIEW — what I would still have to ask

**Written by re-reading this document as if I had never seen the project.**

1. **I do not know how to run the analysis stage end-to-end.** §4.2 says "ROOT-only,
   contract env vars" without naming them. **They are in
   `Validation/TestAnalysisRawInputContract.C` and the analysis submit renderer
   (`tools/render_analysis_submit.py`); read one job's rendered `.sub` from
   HF_PT2_INT for a worked example.**
2. **The species→category derivation is asserted, not specified.** Registry flag
   + spin type gives the category per `HeavyFlavourUtils.h:353-376`
   (`ClassifyHeavyState` / `ClassifyHeavyStateDetailed`). **Read those two
   functions before implementing check 2** — the mapping must reproduce them
   exactly or the check fails for the wrong reason.
3. **"The paper's 11 classes" is my construction, not the paper's.** I derived
   equal-population percentiles; I never located the paper's own boundary
   definition. `status_analysis_qq.C:217,230` and
   `improvedPlotting_THnSparse.C:1211-1214` are the likely authority.
   **Reconcile before anything is quoted.**
4. **The 49× merge cliff has no surviving mechanism.** Chunking was falsified.
   Three constraints are recorded in `POST_SUBMISSION.md` (pure CPU, √N,
   MONASH-only). **It is the only unexplained thing in the pipeline and it
   affects no physics number.**
5. **`resubmit_held.py` has never run on a batch.** One held job is waiting.
6. **The M1–M10 physics review is not in the tree.** Entries cite it; a cold
   reader cannot open it. `RELEASE_BLOCKERS.md` carries an OWNER ACTION line —
   it belongs in `docs/review/`.
7. **`docs/audit/**` are point-in-time records and are deliberately unedited.**
   At least one row (the README tune count) is already stale. **Do not treat the
   audit as current.**
8. **I never verified promoted HF_PT2 data**, and neither did the two handoffs
   before me. It has been taken on trust for six generations.

---

## 10. If you read only one thing

**The campaign is running and healthy. Do not move the Nikhef checkout. Read
hold reasons, never hold counts. Your first job is the granted `config/`
authorization with its version-awareness requirement — and the species axis
lands with its validation or not at all.**
