# Systematics wave 1: pre-registered, and everything generation-dependent is queued — 2026-08-17

**Suite 46/46 → 48/48 (18 new contract tests). Wall clock 10:38–12:0x CEST.**
`stbc-i3` up **4 d 12 h**, boot 2026-08-12 23:06:56 — **no reboot**.

> **Headline: the six-source systematics program is pre-registered and the seven
> generation-dependent campaigns are queued (2100 jobs, Condor
> `5519094`–`5519100`). Two launch blockers were found on the way — the
> production worker and the producer build have BOTH been broken since the
> Aug 12 restructure, and no production job had ever been run from the
> restructured tree. S5 is measured and is an exact zero. The deployment gate
> passed: the rebuilt producer reproduces the nominal event tree across 36.9
> million values. The frozen checkout was never touched.**

---

## 1. The merge — one line, as briefed

Merge `315689` alive at **2 d 20 h 53 m**, supervisor `316182` alive,
`CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` still **absent**, Nikhef
checkout unmoved at **`43e35be8`**. Consistent with the ≈ 18:30 ETA. **No
intervention, and nothing this session ran on `stbc-i3`** — every step ran on
`stbc-i1` (load 0.08, 24 cores) against a separate deploy.

*Noted because it moves the ETA:* `stbc-i3`'s load average rose from 7.6 to
**42** during the session, from other users' work, not ours.

## 2. TWO LAUNCH BLOCKERS — the session's most valuable finding

**Neither would have surfaced until 300 jobs had failed after the queue wait.**
Both are the same defect: the 2026-08-12 restructure moved a file and the thing
that computed its path was not updated. Both were latent for five days for the
same reason — **the Nikhef checkout is still at the pre-restructure commit
`43e35be8`, so no production job has ever been launched from the restructured
layout.** The first one would have been a systematics variation.

| # | what | proof |
|---|---|---|
| **1** | `generation/submit/runCondorJob.sh` derived `project_base` from `dirname $0`, correct only while the script sat at the repository root. It resolved to `<checkout>/generation/submit`, so every job exits 3 at the required-component check | Ran the worker with 15 valid arguments; it printed `required component missing: …/generation/submit/generation/producer/…` verbatim |
| **2** | `generation/producer/Makefile` demanded `GeneratedHeavyFlavourRegistry.h` beside the producer, but both generated headers moved to `generation/registries/`; the producer includes them by bare name, so the path was missing as a prerequisite *and* from the include path | `make build` in the deploy stopped at `No rule to make target GeneratedHeavyFlavourRegistry.h` |

**Both fixes assert rather than only compute.** The worker now fails loudly if it
is not at `<checkout>/generation/submit`, and a test pins the *derivation* rather
than the fix, so the next move of that file fails in the suite instead of on a
worker node. Four dead build rules went with #2 — the split-chain producers moved
to `attic/split_chain/` in the same restructure, so `all` named sources that were
not there and a bare `make` in that directory failed.

## 3. The pre-registration — `docs/SYSTEMATICS_PREREGISTRATION.md`

Committed as `fc59491`, **before the first render**, so the git history is the
evidence that the design preceded the data. Six sources, A2's template, A2's
negligibility ladder reused verbatim (0.1 %, 2 σ, the three-verdict ladder) —
deliberately unchanged, because re-deriving a threshold after seeing that A2's
effect was 0.02–0.23 % would be choosing one with knowledge of the answers.

**Three design choices a reader will want the reason for, so they are in the
document:**

1. **Scale varies `renormMultFac` and `factorMultFac` INDEPENDENTLY** — four
   campaigns, not the cheaper, larger-number coherent two. Because `μ_F` and the
   PDF act on the same object, the initial-state parton flux: a combined scale
   number would entangle S1 with S2 and leave the quadrature rule's independence
   assumption uninspectable. §9.1 registers what to do in either outcome.
2. **PDF alternate is `pSet = 8` (CTEQ6L1)** against the resolved nominal 13
   (NNPDF2.3 QCD+QED LO), both **read out of the installed 8.317 xmldoc**, not
   from memory. Chosen because `α_s(M_Z)` is 0.1298 vs 0.130 — 0.15 % — so the
   variation isolates PDF *shape*. `pSet = 14` was rejected explicitly: same fit,
   `α_s = 0.119`, an 8 % coupling change in a PDF costume that would double-count
   the `μ_R` arm.
3. **pTHat points are the scan's own measured 1.0 and 4.0** about the nominal
   2.0, read from the card (line 47). This closes a limitation the project wrote
   down for itself: the scan's *Limits* section says it does not answer whether
   the conclusion is robust to the threshold. **The asymmetry is registered in
   advance** — 2.0 → 1.0 moves the MB comparison by −24.4 points, 2.0 → 4.0 by
   +54.8 — so it cannot later be reported as a discovery.

**The cost was stated before it was spent:** 2100 jobs, 210 M events, ≈ 193 GB
against 1009 GB free on a filesystem at 97 %. The named lever if the owner wants
it cheaper is dropping the `μ_F` pair, **not** thinning events.

## 4. One registered consequence was improved on, and the registered text stands

§11.2 registered that adding the three varied keys to
`config/tune_difference_allowlist_v1.json` would move
`kTuneDifferenceAllowlistSha256` and leave the 3000 central raw files **not
cross-validatable**. Implementation found that avoidable.

**That digest turned out to be pinned three ways, not one:** by the **frozen**
Gate-B spec, by a suite test asserting the spec pins the checked-out file (it
failed — that is how the third pin was found), and in every raw file's own
metadata. So the keys live in a new `config/systematic_variation_settings_v1.json`
feeding only the audited-key union the producer checks against.

**What that buys:** the tune-allowlist digest is unchanged at `2b35e52a…`, the
frozen spec still pins the file it was frozen against, and the variation raw files
carry the **same** allowlist digest as the central campaign — so they **are**
cross-validatable. The rebuild is still forced (46 → 49 audited keys), so §10.1's
nominal-reproduction check is not weakened.

**Registered text unedited; an annotation in §11 carries the improvement.** The
A2 precedent.

The keys are deliberately **not** in `allowed_tune_differences`, so the cross-tune
audit still requires one varied value shared by all three tunes — which is what a
variation is. A card varying the scale for JUNCTIONS alone is still rejected, and
a test pins that.

## 5. What was built

| | |
|---|---|
| `tools/make_systematic_cards.py` | generates the 21 variation cards from `config/systematics_variations_v1.json`, `--check`-able like the registry generator. **Asserts rather than assumes**: the varied key must be one the producer accepts, every key in the result must be audited, the card must differ from its nominal in **exactly one** key with the declared value, and **the declared value must differ from the nominal's** — so a variation that varies nothing cannot be written. That last check is the failure mode that would have read as a null result |
| `campaign.py::resolve_card_path` | the ONE definition of the card layout; the worker asks it rather than rebuilding the path in bash. `NONE` resolves to exactly the nominal path, so the central campaign's rendering is byte-unchanged |
| `--card-variant` | threaded through renderer → submit row → ClassAd (`+HFCardVariant`) → worker → sidecar |
| `resubmit_held.py` | **derives** the variant from the campaign's own sidecars and refuses a campaign carrying two. Without it a retry would silently draw the nominal card, and the failure would be **invisible** — each such job internally consistent, its card sha matching what it really ran — diluting the variation toward "no systematic" |
| `tools/systematic_class_migration.py` | S5, by re-projection |

**The materialised card keeps the NOMINAL filename with variant CONTENT**, because
the producer derives its settings filename from the tune
(`heavyflavourcorrelations_status.cpp:144`). **The producer needed no change at
all.**

## 6. S5 — measured, an exact zero, and its input re-measured

> **Every one of the eleven classes is structurally insensitive, in both arms,
> for all three tunes. Δ(c) = 0 exactly — not "consistent with zero".**

`N_ch` is a count, so an integer; the boundaries are half-integers, deliberately
("so no integer `N_ch` is ambiguous"); a per-class observable is therefore a sum
over a set of integer `N_ch` bins, and a boundary move changes it **only if it
crosses an integer**. None does. **Block SEMs are exactly zero** and that is the
correct treatment, not a missing number: the same operator on the same events
gives an identically zero per-block difference for *any* block decomposition.

**Checked on real data as well as argued.** Re-projecting the three committed MB
samples (513 079 events, integer `N_ch` 0–175) under both shifted boundary sets
moves **zero** integers between classes and changes **zero** class populations.
Max |relative Δ| = 0.000e+00.

> ### The margin was thin on the registered input, so the input was re-measured
>
> `c11` at 32.5 needs a **1.538 %** shift to cross an integer. The **8.315** bias
> was **1.327 %** — a margin of **1.16**, i.e. 16 %, carrying an entire systematic
> source on a superseded generator version. `NCH_CALIBRATION_20260730.md` predates
> the 8.317 migration, so the production-policy figure had never been measured on
> the generator production uses.
>
> **Re-measured on 8.317 this session: the bias is 0.767 %, and the margin is a
> factor of 2.01.** 200 000 events per arm, both arms paired on the macro's fixed
> seed so the shared event content cancels. Experimental convention **7.040**,
> production policy **6.986**. Both arms rose from 8.315, but the production-policy
> arm rose four times as much, which is what closed the gap. Full result in
> `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md`; the tool's constants are
> updated with the 8.315 pair kept beside them, so the supersession is visible in
> the source that depends on it.
>
> **The null is now comfortable rather than fragile**, and the boundary above which
> this bias would migrate a class moves from 37.7 to **65.2**.

Also recorded: **any boundary above 65.2 would be migrated by this bias**, so a
future re-binning does not inherit the null. The tests are where that surfaces —
they assert the per-boundary margin exceeds the measured bias, so a re-binning or
a re-measured bias that breaks the null fails the suite instead of leaving a stale
"exactly zero" in the result document.

**What the zero does not cover:** the bias still shifts the *percentile labels*
the classes carry, so the paper's classes correspond to slightly different
experimental percentiles than their labels claim. A **labelling caveat for the
paper text**, not a per-class uncertainty, and this source must not be presented
as covering it.

## 7. The deploy, and why a clone rather than the A2 pattern

| | |
|---|---|
| deploy | `/data/alice/ipardoza/systematics_deploy/Hadronization`, a **real git clone**, tracked-clean |
| deploy commit | `72ca4e3913da25be675dc2f968151ea68f9b8b87` |
| producer | rebuilt there, sha256 `379b449d…`, **zero warnings**, 21 s |
| transfer | a 56 MB git bundle over scp — the Nikhef repo's own `.git` is **23 GB**, so cloning from it was never an option |
| seeds | `tools/campaign.py`, ordinals **4–10**, burned at render into the authoritative ledger, **3557 → 5657** |
| ledger safety | that ledger is **untracked and git-ignored** (`.gitignore:92`), verified before writing, so appending to it does not dirty the frozen checkout |

**The brief said to inject the deploy commit via environment, the A2 lesson. I
did not, and the reason is worth recording.** A2's analysis deploy was a `git
archive` with no `.git`, which is *why* it needed
`HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT`. The production worker's commit check is
a **verification**, not a label — it compares `git rev-parse HEAD` against the
submit file's value and refuses a tree with tracked modifications. A clone keeps
that guard doing its job; env injection would have reduced it to an assertion.
**Nothing was weakened to run these campaigns.**

## 8. Launch, and the staged release

Seven campaigns, `hold = True`, cluster ids from the submit output via `tee`
(`submit_logs/*_submit.log` in the deploy), never from a queue scan:

| campaign | ordinal | variant | cluster |
|---|---|---|---|
| `HF_SYS_MUR_UP` | 4 | `mur_up` | **`5519094`** |
| `HF_SYS_MUR_DOWN` | 5 | `mur_down` | **`5519095`** |
| `HF_SYS_MUF_UP` | 6 | `muf_up` | **`5519096`** |
| `HF_SYS_MUF_DOWN` | 7 | `muf_down` | **`5519097`** |
| `HF_SYS_PDF_CTEQ6L1` | 8 | `pdf_cteq6l1` | **`5519098`** |
| `HF_SYS_PTHAT_1` | 9 | `pthat_1p0` | **`5519099`** |
| `HF_SYS_PTHAT_4` | 10 | `pthat_4p0` | **`5519100`** |

**21 distinct effective card sha256, none equal to any nominal** — checked before
submitting, not after.

### First-output verification, from the generator's own mouth

**The strongest available form of pre-registration §10.2** — not the card, the
resolved value. PYTHIA's own settings dump in each pilot's `.out`, current value
against PYTHIA's default:

```
HF_SYS_MUR_UP        SigmaProcess:renormMultFac   2.00000  (default 1.00000)
HF_SYS_MUR_DOWN      SigmaProcess:renormMultFac   0.50000  (default 1.00000)
HF_SYS_MUF_UP        SigmaProcess:factorMultFac   2.00000  (default 1.00000)
HF_SYS_MUF_DOWN      SigmaProcess:factorMultFac   0.50000  (default 1.00000)
HF_SYS_PDF_CTEQ6L1   PDF:pSet                     8        (default 13)
```

The PDF line confirms **both** ends of the S2 variation at once: the alternate is
8 and PYTHIA's own default is 13, exactly as pre-registered.

Seeds `140000001 / 150000001 / 160000001 / 170000001 / 180000001` — ordinal ×
10⁷ + base, as `seed_derivation_v2` requires.

**The first promoted output passed everything:**

```
state = PASS   validator_status = 0
RAW_VALIDATION_SUMMARY errors=0 entries=100000 process_codes=4 stability_rows=219
```

with the full chain intact in the receipt — campaign `HF_SYS_MUR_UP`, ordinal 4,
seed 140000001, card sha `12d206ab…` (the **variant's**), producer sha
`379b449d…` (the **rebuild's**), commit `72ca4e39` (the **deploy's**).
**The rebuilt raw validator accepts output from the rebuilt producer**, which is
the first evidence that the 49-key registry change is self-consistent end to end.

Elapsed 264–350 s per MONASH job, against the documented 247 s median / 321 s max
— so the 3600 s hang guard has ample headroom.

**The release was staged on the real risk, not uniformly.** The five nominal-pTHat
campaigns were bulk-released once two had promoted `PASS` (1500 jobs). **The two
pTHat campaigns were deliberately held** beyond their pilots, because
`ValidateRawOutput.C:603` fails closed on `PhaseSpace:pTHatMin does not match
authorization` — the one check that could reject an entire pTHat campaign — and
that check had never been exercised away from 2.0.

**Both arms then cleared it and were released.** `phase_space_pthat_min` = 1.0 and
4.0 in the receipts, `state PASS`, `errors=0 entries=100000`, and PYTHIA's own
dumps reading `1.00000` and `4.00000`. **All 2100 jobs are released**, and the
jobs held in the meantime carried `HoldReason = "submitted on hold at user's
request"` — **no faults anywhere in the 2100**.

> ### ⛔ The deploy must not move
>
> Every one of the 2100 jobs verifies commit `72ca4e39` at startup and refuses a
> tree with tracked modifications. **Do not check out, pull or edit tracked files
> in `/data/alice/ipardoza/systematics_deploy/Hadronization` until the campaigns
> finish.** Later commits on `physics-focus` are harmless — they are simply not in
> that deploy, which is the point. A macro needed mid-campaign was copied to
> `/data/alice/ipardoza/systematics_regression/` rather than added to the deploy,
> for exactly this reason.

## 9. Boundaries respected

No consolidation work. No analysis-checkout change. No `Paper/**`. **S4 is
pre-registered and NOT launched** — its jobs would pin the old head and re-block
the checkout advance. Nothing ran on `stbc-i3`. The merge, its guards and its
pinfile were untouched; the only write anywhere near the frozen checkout is the
append-only git-ignored seed ledger.

### ⚠ One error of mine, in the git history and not in the physics

**`fc59491` — this session's pre-registration commit — contains six file
deletions that belong to the concurrent triage session.** I staged one file
(`git add docs/SYSTEMATICS_PREREGISTRATION.md`) and then ran `git commit` with
**no pathspec**, and `git commit` commits the whole index, not the part one
session staged. The triage session had `git rm`s pending, so they rode along:
`attic/count_events/CountEvents/{count_events.sh,count_events_bb_cc.C}`,
`attic/plotting/{ListHistos.C,PlottingWizard.C,combinedCanvasPlots.C}`,
`attic/reproduceCanvasPadError.C`.

**Nothing was lost and nothing unintended was deleted** — all six are attic files
the other session intended to remove and documented in `docs/REMOVALS.md`, so the
tree is in the state both sessions wanted. **Only the attribution is wrong**: the
deletions sit under a commit message about pre-registration, and `7143c8b` then
documented removals whose deletions had already landed.

**It is NOT being rewritten.** `72ca4e39` descends from `fc59491`, and 2100
in-flight jobs verify that commit at startup; rewriting history under them would
fail every one. The audit is recorded here instead: every other commit of this
session (`b43599b`, `72ca4e3`, `ac3b42d`, `cf9c7ef`, `a4d82c6`, `e933e01`,
`4f7948a`) contains only this session's own files, checked file by file.

**A concurrent session is writing to `physics-focus`.** `7143c8b` (the
documentation-triage session, 11:04) landed between this session's first and
second commits. Documentation only — 9 files, no code, no card, no tool my program
calls — and every dependency of this program was verified present afterwards, with
the suite at 48/48. **The deploy is insulated by construction:** it is a separate
clone pinned at `72ca4e39`, so the 2100 in-flight jobs cannot be affected by
further commits to the branch.

## 10. THE CHECKOUT-ADVANCE DETERMINATION — for Consolidation A

> ### ✅ RULED, second addendum 2026-08-17 — this section is the cited determination
>
> **1. The advance does not wait for the systematics campaigns.** Zero in-flight
> jobs pin `43e35be8`; all 1976 ClassAds name the separate deploy. **This is a
> measured fact, not an override** — nothing was overridden, and the guard's
> queue branch was never the operative one (see below).
>
> **2. The pinfile's recorded protocol is INVALID.** It names dead PID `3675829`
> and `merge_v3.log`; the reboot made both clauses read as satisfied while the
> merge lives. **Operative condition:**
> `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` **present** *and* PID
> **`315689`** exited cleanly.
>
> **3. The gate session REFRESHES the pinfile** to state that condition —
> superseded content preserved and dated — **before any removal**. Removal only
> under the corrected condition. **Not done by this session**: the action is
> assigned to the gate session, and this session does not own the merge.
>
> **4. Recorded as `docs/ERROR_RECORD.md` E8**, with the supervisor's
> completion-blindness as the mirror-image second instance.

**The ruling this section was written to answer:** if `make can-advance` refuses on
account of the 2100 systematics jobs, read what the jobs *actually* pin; if only
the separate deploy, either wait for convergence or proceed on the documented
determination; if **any** job pins `43e35be8`, wait.

### What the jobs pin — measured from the queue's own ClassAds

```
HFRepositoryCommit    1976  72ca4e3913da25be675dc2f968151ea68f9b8b87
Cmd                   1976  /data/alice/ipardoza/systematics_deploy/Hadronization/
                              generation/submit/runCondorJob.sh
jobs pinning 43e35be8:   0
```

**Zero of the in-flight jobs pin the analysis checkout, and none of them executes
out of it.** All 1976 remaining pin the separate deploy at `72ca4e39` and run that
deploy's worker. On the jobs' account, the ruling's *proceed* branch applies and
the *wait* branch does not.

### ⛔ BUT THE JOBS ARE NOT THE BLOCKER, AND NEVER WERE

**`make can-advance` will refuse for a different reason, and that reason is
explicitly not overridable.** `tools/checkout_advance_guard.py` checks the
**pinfile before it consults the queue at all**:

> *"THE PINFILE OUTRANKS EVERYTHING, INCLUDING THE OVERRIDE … This is NOT
> overridable."*

`/data/alice/ipardoza/Hadronization/.git/checkout_pin` **is present** (created
2026-08-10 23:07) and names the v3 full-scale merge. So the refusal a consolidation
session sees is the pinfile's, not the systematics jobs'. **Reading the jobs'
pin target answers the question the ruling asked and does not unblock the
advance.**

### ⚠ AND THE PINFILE'S OWN REMOVAL CONDITION IS NOW A TRAP

This is the finding that matters most here. The pinfile says to remove it only
after **both**:

> *1. the log contains 33 `PROMOTED_MERGE` lines, and 2. PID `3675829` has exited.*

**Both now read as satisfied while the merge is demonstrably alive:**

| condition | literal check | reality |
|---|---|---|
| PID `3675829` exited | **ABSENT** → reads as satisfied | killed by the **2026-08-12 reboot**, not by completion. The merge was restarted twice and is **alive as PID `315689`**, 2 d 21 h elapsed |
| the named log has 33 `PROMOTED_MERGE` | `merge_v3.log` has **15** | the live run writes **`merge_v6.log`** (18), and 15 + 18 = 33 — the legs *are* all merged, but only if you sum across logs the pinfile does not name |

**The pinfile anticipated the time trap** — "time is not the condition, completion
is" — **but not the restart trap.** It pins a PID and a log path, and the reboot
invalidated both. A consolidation session following its instructions literally
would remove it and advance while `315689` is reading the tree, in its redundant
closure phase, which emits no further `PROMOTED_MERGE` lines.

**LEAVE THE PINFILE IN PLACE.** Its own words settle it: *"If the date above has
passed and the merge is still running, the merge wins: leave this file in place. A
stale-looking pin costs a delayed rebase; a removed one costs a 65 h run."*

**The removal condition that is actually correct** — ratified as operative by the
second addendum, and neither clause is in the file:

1. `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING` is present — **still
   absent** at 12:38 CEST — **and**
2. **PID `315689`** has exited cleanly (not `3675829`), **on `stbc-i3`**.

**Merge state at 12:38, on the final leg.** MONASH and JUNCTIONS closure markers
are both present; `ValidatePairBlockClosure.C(…CLOSEPACKING…)` is running as PID
`1516311`. Merge `315689` alive 2 d 21 h 56 m, supervisor `316182` alive, EOL
watcher `2566164` alive and correctly **not** fired. Consistent with the ≈ 18:30
ETA.

> **The host clause is not decoration.** A check of `ps -p 315689` run from
> `stbc-i1` returns **absent**, because the merge is on `stbc-i3` — this session
> did exactly that and read a death for about a minute before catching it. An
> identity checked in the wrong context is indistinguishable from one that has
> exited. Recorded as the third facet of `ERROR_RECORD.md` E8.

**The completion fact comes first and is authoritative.** That ordering is not
cosmetic: absence of the PID *without* the marker is a death, not a completion,
which is exactly how the reboot produced the trap. It is also the condition
`tools/supervisor_eol_watch.sh` already uses for the mirror-image guard, five days
after the pinfile was written.

**The refresh is the gate session's action, not this one's.** This session
recorded the trap and left the file untouched; amending a guard artifact for a run
it does not own is the wrong direction. The owner has since assigned the refresh to
the gate session, to be done **before any removal**, with the superseded content
preserved and dated.

---

## 11. For the next session

> ### Both of the session's late verifications LANDED, and both PASSED
>
> **1. The 8.317 decay-policy re-measurement — S5's input was wrong, and in the
> good direction.** 200 000 events per arm, both arms paired on the macro's fixed
> seed `20260730`, on `stbc-i1`. Experimental convention **7.040**, production
> policy **6.986**, so the bias is **0.767 %** against the 8.315 value of
> **1.327 %** — **42 % smaller.** S5's margin against `c11`'s 1.538 % edge goes
> from **1.16 to 2.01**: the null is comfortable rather than fragile. The boundary
> above which this bias would migrate a class moves from 37.7 to **65.2**.
> Written up in `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md`, the tool's
> constants updated with the 8.315 pair kept beside them so the supersession is
> visible in the source that depends on it, S5's result regenerated, suite 48/48.
>
> **A consequence beyond S5: the paper's number changes.**
> `docs/DESIGN_AND_RATIONALE.md` §3.5 and `NCH_CALIBRATION_20260730.md` both state
> the decay policy "costs 1.3 %", and §3.5 records it as the one consequence the
> paper is required to state. **On the production generator it is 0.77 %.**
> The same disposition `PTHAT_MULTIPLICITY_SCAN_8317.md` reached for the "36 %
> below minimum bias" claim applies here.
>
> **And the report carries the input S4 will need**, measured on 8.317 rather than
> inferred: the `|η|<4` and `|η|<1` counters together, 51.201 vs 12.948, agreeing
> to **1.1 %** per unit η.
>
> **2. Pre-registration §10.1, the nominal-reproduction gate — PASS.**
>
> ```
> values compared:    36900000 vs 36900000
> event tree digest:  a6683ddd8ccae257 vs a6683ddd8ccae257
> EVENT TREE IDENTICAL -- every value, every entry
> NOMINAL_REPRODUCTION PASS metadata_fields_differing=7
> ```
>
> 36.9 million values, 110 leaves, 100 000 events, one digest. **The
> registry-header change did not reach the event loop**, so variation numbers from
> this deployment may be believed. All seven metadata differences are expected:
> `executable_sha256` (the rebuild), `repository_commit` (the deploy),
> `condor_cluster` (run by hand), and four timing/memory fields.
>
> **`tune_difference_allowlist_sha256` is NOT among them, and that confirms §4's
> design decision end to end**: the variation raw files carry the same allowlist
> digest as the central campaign's 3000, so the two sets remain
> cross-validatable — which the registered plan had said they would not be.
> Neither `effective_settings_sha256` nor `effective_settings_entries` differs
> either, so the 46 → 49 change writes **nothing** into the raw metadata; the
> file-size difference (92 200 277 vs 92 200 782 bytes) is the differing strings
> alone. **Not byte-identical**, which is precisely why the bar was content rather
> than a checksum.
>
> **One bug in my own comparison, found by checking a prediction rather than
> reading a green result.** The first run reported four differing metadata fields
> and did **not** list `executable_sha256` or `repository_commit` — which *must*
> differ. Cause: the string branches were read through a local `std::string` whose
> address was handed to `SetBranchAddress`, and ROOT replaces that pointer with its
> own buffer, so every string compared `""` to `""`. A silent false negative on
> exactly the fields the check is about. Fixed to read through ROOT's pointer, and
> re-run gave the seven above. **The event-tree digest was never affected** — it
> reads numeric leaves — so the load-bearing half of the check stood throughout.

1. **The analysis stage for these campaigns is not built.** Raw output is not a
   result; the two deliverables — decomposition fractions and per-class OS−SS —
   need the extraction/analysis chain pointed at seven new campaigns.
2. **S4 launches after the checkout advance** (`STATE.md` PENDING #5). Its
   percentile-preserving boundary translation now has a measured 8.317 input: the
   two counters agree to 1.1 % per unit η (`NCH_DECAY_POLICY_BIAS_8317.md`).
3. **The paper's 1.3 % decay-policy sentence is now wrong** — it is 0.77 % on the
   production generator. `docs/DESIGN_AND_RATIONALE.md` §3.5 and
   `NCH_CALIBRATION_20260730.md` both carry it. Not touched this session: the
   brief excluded `Paper/**`, and §3.5 is a design document whose amendment is a
   separate decision.
4. **Disk.** ≈ 193 GB of the 998 GB free will be consumed. `STATE.md` PENDING #7
   (consolidation) is now load-bearing rather than optional.
5. **Do not move the pinned deploy** until the 2100 jobs finish — see §8.
