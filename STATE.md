# State — frozen, pending, not planned

**As of 2026-08-16.** The one-screen answer to *"where is this project?"*

**The harvest is done.** All three tunes have merged 10/10 blocks, all three
closures have PASSED, and the three-tune central table — the resubmission's
central number — is **FINAL** in
[`docs/THREE_TUNE_CENTRAL_TABLE.md`](docs/THREE_TUNE_CENTRAL_TABLE.md). What
remains is the figure set, the consolidation phase, and one open ruling (the I2
flags, PENDING #2).

> ### ✅ THE FREEZE IS LIFTED — 2026-08-17 20:12 CEST
>
> The merge completed 16:16 CEST with all three closure markers, the pinfile was
> refreshed and removed, the queue drained, and **the checkout advanced
> `43e35be8` → `8650a047` on a clean gate with no override.** The five-day
> freeze — during which no production job had ever run from the restructured
> layout — is over.
>
> **Nikhef is at `8650a047`, which was local `HEAD` at the moment of the
> advance.** Commits made *after* it — this session's record, which could only
> be written once the advance had happened — sync on the next advance, once the
> three retry jobs (`5526031`–`5526033`) leave the queue. **The two trees agree
> on every line of code; they differ only by trailing documentation.**

*(Superseded, kept for the reader of an older handoff: "The freeze still
stands. The merge process is still running its own redundant closure pass, so
the pinfile is intact and the Nikhef checkout is unmoved at `43e35be8`.")*

Full measurement discipline applies only to results the paper quotes; operations
get ordinary engineering care.

---

## FROZEN — recorded, digest-pinned, not to be recomputed

Every entry below has its digest and its regeneration recipe in
[`docs/GOLDEN_OUTPUTS.md`](docs/GOLDEN_OUTPUTS.md).

### The species axis — the spine

**202 species, digest `646f310f78126267`.** Asserted by all three decay maps, by
the v3 closure's `species_ordinal_digest` invariant, and in-file on every merged
output. **If this moves, everything below is void.**

### The decay-parent maps

| map | internal `map_sha256` | status |
|---|---|---|
| v1 | `e343fd88…` | **history — defective**, does not conjugate antiparticle decays (`ERROR_RECORD.md` E1). **Never delete: it is the evidence** |
| v1.1 | `dd502a10…` | the conjugation fix |
| **v2** | `c9593c9c…` | **current** — adds the two species-level splits |

Both rebuild from committed probe anchors with committed tools, in seconds, with
neither ROOT nor PYTHIA.

### MONASH — the first tune's central numbers

> **⚠ SUPERSEDED 2026-08-13 — the shares in this table are biased.**
> `docs/ERROR_RECORD.md` **E5**: the trigger-owned closure was counted once per
> pair file (24× charm, 26× beauty). Corrected: kCentralGround **52.4958**,
> kExcludedVector **46.4946**, kExcludedExcited **1.0095**; total
> **53,662,414 … 53,662,828**. The block SEMs below are **not** corrected —
> they were computed on the replicated product and a live re-extraction is
> pending.
>
> **✅ RE-EXTRACTED 2026-08-13 — the reconstruction is superseded by measurement.**
> Central + ten blocks, fixed extractor, ROOT 6.30/01 on pin. **Total
> 53,662,416** (inside the predicted bracket, 2 counts above its floor);
> kCentralGround **52.4959 ± 0.0074**, kExcludedVector **46.4946 ± 0.0079**,
> kExcludedExcited **1.0095 ± 0.0012**; charm : beauty **89.9852 : 10.0148**,
> exact against prediction. **I3 exact and I2 clean (0 flags in 10).** The SEMs
> here are now the deduplicated ones. Per event: **0.5366**, against the
> replicated 12.9866. **`docs/MONASH_CENTRAL_TABLE.md` §0 is the table of
> record.**

`docs/MONASH_CENTRAL_TABLE.md`. **Closure PASSED at the registered counts:
2100 content / 1500 invariant, errors = 0**, schema resolved from each file's own
`analysis_schema`. **I3 exact** — the ten blocks sum to the central,
1,298,655,240 entries, bin by bin — which establishes that the addition is
exact, **not** that the entries are unique (E5).

| diquark-structure (a partition, sums to 100 %) | block mean % | SEM |
|---|---|---|
| kCentralGround | **52.3388** | 0.0074 |
| kExcludedVector | **46.6510** | 0.0079 |
| kExcludedExcited | **1.0102** | 0.0012 |
| kMultiplyHeavy | **0.0000** | 0.0000 |

**Experiment-comparable (map v2) — a SELECTION, not a partition; these do not
sum to 100 %:** D⁰ 25.2435 ± 0.0038, D̄⁰ 25.1707 ± 0.0070, D⁺ 13.1408 ± 0.0034,
D⁻ 13.1129 ± 0.0032, D_s⁺ 4.2366 ± 0.0015, D_s⁻ 4.2331 ± 0.0017,
B⁺ 2.3035 ± 0.0018, B⁻ 2.3024 ± 0.0026.

> **Two labels travel with this table wherever it is quoted.**
>
> **`kMultiplyHeavy` is ~0 because doubly-heavy baryons are rare, not because
> anything is excluded** — 192 entries of 1,298,655,240. It is a populated
> category *inside* the partition (Ξ_cc, Ω_cc, Ω_ccc; `|q_c| > 1` or
> `|q_b| > 1`), and the six categories sum exactly to the total. **B_c⁺ is not
> there — it is `kCentralGround`, inside the primary bin.** The one category
> excluded by construction is **`kHiddenHeavy`** (quarkonia), with exactly zero
> entries; `kOtherNoncentral` is likewise empty, being unreachable for any
> open-heavy species.
>
> **The experiment-comparable table is a selection.** Its rows are the largest
> observables a detector reconstructs, not a complete decomposition. A reader who
> sums the column and finds less than 100 % has not found missing weight.

### M7 — the unresolved-origin diagnostic, INCLUSIVE LEVEL, both sectors

> **RELABELLED 2026-08-13 (review finding A2).** These are **inclusive-level**
> numbers: rate of unresolved-origin open-heavy hadrons, and the shift in the
> **inclusive** baryon fraction. The macro's only cut is
> `heavyIsFinal && q_sector != 0` — no primary, ground-state, acceptance,
> trigger-pT, multiplicity, pair or OS−SS selection.
>
> **They are NOT a bound on the pair observable's systematic**, and must not be
> cited as one. A global rate cannot bound a multiplicity-localized OS−SS
> effect. The pair-level measurement is **pending** — see below.

| | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| **charm**, inclusive relative shift % | 0.0451 ± 0.0008 | 0.5497 ± 0.0019 | 0.5125 ± 0.0024 |
| **beauty**, inclusive relative shift % | 0.0141 ± 0.0011 | 0.0140 ± 0.0008 | 0.0143 ± 0.0007 |

**Charm's inclusive shift is tune-dependent by an order of magnitude; beauty's
is flat** — beauty moves all three tunes by the same 0.014 %, so at inclusive
level it cannot bias a tune comparison. **That statement does not carry over to
the pair observable**, where the selection and the multiplicity binning are
both different. Both sectors' block logs are committed
(`anchors/m7_blocks/`, `m7b_blocks/`).

### Σ_b ordering — the physics gate, passed

Σ_b **26.59 % ± 0.24**, Σ*_b **10.51 % ± 0.19**, ground **0.83 % ± 0.11**, at
1000 files. R1 HIT; R3 for Σ*_b HIT (+1.47 % ± 0.47, +3.2 σ); Σ_b null.

### The second-branch number

**0.0018 %** — species-level, after the two map-v2 splits. **C6 (residual < 1 %)
passes by a factor of ~550**; the residual is B_c± alone. The historical
**12.84 %** survives as an honest upper bound on a question the v1 artifact could
not answer. ~~**Quote 0.0018 %.**~~

> **UPDATED 2026-08-13.** The claim had **no committed derivation** and was at
> risk of withdrawal. It is now **implemented and confirmed**:
> `second_branch_weight.py --v2-map` (recipe R8b) reproduces 5.7737 % pre-split,
> 0.0018 % post-split, **and** the per-species split B_c⁺ 0.000903 / B_c⁻
> 0.000896 — three published quantities at once, none of them fitted.
>
> **On the E5-corrected weights it is 0.0017 %** (B_c⁻ 0.000838, B_c⁺ 0.000819):
> the residual is carried entirely by B_c±, a **mixed** beauty-charm species, so
> it moves under the deduplication. **Quote 0.0017 % against the re-extracted
> table**, 0.0018 % only when quoting the replicated-era one. C6 passes by ~590.

### The campaign

**HF_RUN3_V1 complete and promoted: 3000/3000.** Seed ledger **3557/3557**
burned, recorded in the campaign-control checkout on Nikhef. Producer sha256
`e54b27bb9e3f…`, present in all 300 analysis outputs. PYTHIA 8.317 and
ROOT 6.30/01 pinned and asserted.

> ### 🔒 SEALED AND AUTHORIZED — 2026-08-17
>
> **`status: canonical`, `publication_eligible: true`**, in both
> `config/dataset_selector.json` and `config/dataset_selector_hf_run3_v1.json`,
> citing `docs/HF_RUN3_V1_PUBLICATION_AUTHORIZATION.md` by sha256.
>
> Sealed on facts re-measured that day, not inherited: **3000** raw / sidecars /
> receipts / `raw_validation` job dirs; merge **33/33** where the summed and
> **distinct** leg counts agree; **one closure PASS per tune** whose verdict line
> is byte-identical between the merge's own pass and the independent runs; and a
> freeze whose seal-recorded manifest sha matches the file, whose ten block files
> sum to 3000 rows, and whose checksums matched the bytes on disk in a
> **12/12 spot-check**. The freeze artifact dates from 2026-08-09 and was
> **validated, not rebuilt** — the builder refuses to overwrite one.
>
> **Eligibility is necessary, not sufficient.** Every figure still owes its own
> house contract, and `docs/FIGURE_INVENTORY.md` §6.3b records a freeze-contract
> defect that still blocks the two raw-reading figure families.

### The systematics campaigns

**HF_SYS_* COMPLETE: 2100/2100**, 2026-08-17 — seven campaigns × 300 raw files,
queue empty, zero held. **The harvest is a separate session and has not begun.**

---

## PENDING — known, in flight, nobody needs to plan it

> # ✅ ALL 33 LEGS MERGED; ALL THREE CLOSURES PASSED — 2026-08-16
>
> **The three-tune table is FINAL** — `docs/THREE_TUNE_CENTRAL_TABLE.md`.
> JUNCTIONS closure PASSED 2026-08-16 11:58:20 CEST, CLOSEPACKING 11:37:27, each
> `errors=0` at **2100 content / 1500 invariant**, schema
> `paul_pair_objects_primary_ground_v3`, verdict lines recorded verbatim in that
> document's §0b. MONASH PASSED 2026-08-12. **Both new closures were run
> independently of the merge**, launched 2026-08-15 22:08 with the strong
> `expected_central_events=100000000`; the merge's own sequential pass
> corroborated MONASH at 12:39 and was still working through JUNCTIONS.
>
> **The merge campaign is NOT yet complete.** PID `315689` is alive and inside
> its own redundant closure phase (~25 h remaining). The freeze therefore
> stands: **pinfile intact, checkout unmoved at `43e35be8`.**
>
> *(History: the merge was killed by the scheduled-maintenance reboot at
> 2026-08-12 23:07 at 15/33 — clean shutdown, kernel `687.26.1 → 687.36.1`,
> matching the Jul 8 / Jul 16 / Aug 12 ~23:0x pattern — restarted 08-13 07:24,
> then restarted once more 08-14 14:42 as `merge_v6.log`. The driver
> re-validates promoted legs rather than redoing them.)*

| # | item |
|---|---|
| 1 | ✅ **DONE 2026-08-16 — the three-tune cross-tune table with block SEMs, the resubmission's central number.** All three tunes FINAL, both conventions, common row set, block SEMs dof = 9. `docs/THREE_TUNE_CENTRAL_TABLE.md` |
| 2 | ✅ **DONE 2026-08-16 — the JUNCTIONS and CLOSEPACKING harvests.** Closure PASS both, I3 exact both, decomposition delivered. **One item still open: the owner's ruling on the I2 flags** (3 JUNCTIONS, 1 CLOSEPACKING) against step 2's registered zero — diagnosed, bounded, jackknifed immaterial at < 1.19 SEM, but the pre-registration's expectation is unmet and the promotion was scoped to the closure verdicts. `THREE_TUNE_CENTRAL_TABLE.md` §3d and §7 |
| 3 | ✅ **DONE 2026-08-13** — the I2 null recalibration. The null is a required argument, I2 uses MAD, the pinned E4 test names binomial explicitly. **The ruling's predicted numbers did not survive measurement and the measurement is recorded instead** (`GOLDEN_OUTPUTS.md` §2.11a) |
| 4 | ✅ **SCORED 2026-08-13 — MISS, closed.** 15 legs in 48.6 h (8.35 h one-time gate + 40.25 h merge work, ~2.68 h/leg) projects to ~97 h against a 65–77 h ceiling; cause closure/merge CPU contention; additionally interrupted by the reboot at 15/33. `docs/MERGE_V3_BAND_VALIDATION.md` |
| 5 | ✅ **DONE 2026-08-17 20:12 CEST — the Nikhef checkout advance is TAKEN.** `43e35be8` → **`8650a047`**, 153 commits, fast-forward, **`make can-advance` passed CLEAN with no override** (`CHECKOUT_ADVANCE_ALLOWED queue verified empty`). The guard hook logged the allow itself, after three recorded refusals. **Nikhef is at `8650a047` — all code identical; local carries only the trailing session record, which syncs next.** Post-advance: suite **49/49 on Nikhef** — the first green run ever from the restructured tree there — guard suite 7/7, and the installer fix passed its first real test (below). Procedure: `docs/CHECKOUT_SYNC_PROCEDURE.md` |
| 6 | **Advisory step 2** — per-tune b-baryon ratios, one table |
| 7b | **A9 — the stale paper table.** ANSWERED 2026-08-13: **not** regenerable from existing artifacts. Receipts, `attempt_metadata`, validator logs and M7 logs carry provenance, origin accounting and a baryon/meson split — no per-species yields and no valence sums. Needs a counting pass over all 3000 raw files, ~10 Condor jobs of ~15 min (M7 pattern). **Deliberately not submitted**: A2 is ahead of it in a full queue. `docs/A9_PAPER_TABLE_REGENERATION.md` |
| 7 | **Disk consolidation** on Nikhef — reshaped to a mapping exercise, not a move: `docs/NIKHEF_DISK_INVENTORY.md` §7 |
| 8 | **The pair-level unresolved-origin systematic** — the real one. **RUN 2026-08-13.** Regression gate **PASSED**: 300 files, 300 diffs, every one the single allowed `analysis_macro_sha256` field, zero unexpected. Campaign re-run as `5486752` after ERROR_RECORD **E7** removed a per-job guard that was selecting on the outcome variable in one arm. **Exposure measured** over 10 M events per tune: MONASH **6.2**, JUNCTIONS **1 219.4**, CLOSEPACKING **1 228.7** restorations per M events — a **≈197×** CR/MONASH ratio against M7's **13.6×** inclusive ratio, which is direct evidence M7 is not a proxy for this. **Δ MEASURED**, and the **TIE-BREAK ROBUSTNESS CHECK RUN** (variation `4e491134…`, regression **PASS**, campaign `5489612`, 300/300 promoted). **LEAD WITH THE SHAPE: Δ rises 5.9–9.7× across the multiplicity classes under BOTH tie-break rules.** That robustness is what makes per-class quoting mandatory — an integrated number is wrong about the shape no matter which rule is chosen — and it means the flat outcome named in advance as legitimate did NOT occur, so **A2's concern is confirmed, not retired**. **THE SYSTEMATIC TO QUOTE (owner ruling): the LARGEST-index arm, PER CLASS**, per cent — JUNCTIONS 0.0255 (M1), 0.0691, 0.1007, **0.1509** (M4), 0.1369 (M5); CLOSEPACKING 0.0377 (M1), 0.1012, 0.1571, 0.1777, **0.2293** (M5); **MONASH NEGLIGIBLE** (≤ 0.004). Integrated values (0.0583 / 0.0795) understate the worst class by 2.6× / 2.9× and must not be substituted. **The smallest-index arm is the cross-check, not a lower bound**: it establishes **rule dependence**, the two orderings differing by **2.0–5.5×** in all ten CR classes at 2.7–21.6 σ. **NOT an envelope** — what is quoted is *the larger of two extremal orderings of `heavyIndex`*, and **neither bounds the space of resolutions**: a pT-ordered rule would give more, which is exactly why the pre-registration rejected it as inflating by construction. **METHOD FINDING** (a result, not a scoring footnote): smallest-index was chosen on the reasoned assumption that `heavyIndex` is uncorrelated with trigger survival; both arms restore an **identical** number of rows, so 2–5× different Δ falsifies it. Registered text unedited; the annotation carries it. "< 0.07 % everywhere" is **RETIRED**; max is **0.23 %**. MONASH's exact zero is *explained, not contradicted* — same 62 restorations, different winners, Δ = 0.0006 ± 0.0002 %. `docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md` and `A2_DELTA_RESULT.md`; `docs/A2_PAIR_UNRESOLVED_{PREREGISTRATION,RUN_RECORD}.md` |
| 9 | ✅ **DONE 2026-08-13** — MONASH re-extracted with the deduplicating extractor, central + ten blocks. **Total 53,662,416, inside E5's predicted 53,662,414…828; charm : beauty exact at 89.9852 : 10.0148.** I3 exact, I2 clean (0 flags), block SEMs recomputed. `MONASH_CENTRAL_TABLE.md` §0 |
| 10 | ✅ **DONE 2026-08-13** — the E5 trap is closed **at the path the chain actually calls**. `tune_extract.sh:15` pointed at `sigmab_runs/task22/`, not the top-level copy; both old readers (`b67f9008…`) are archived in `attic_e5_replicating_extractor_20260813/` with a manifest and the fixed reader (`4cd8b6fa…`) is installed at both. The chain also passed **no `--registry`** and **map v1.1**, both fixed. Proven: the chain's exact invocation on MONASH block_1 is **byte-identical** to the committed anchor |
| 12 | **QUEUED, NOT BUILT — the advance guard's queue branch should check WHICH commit in-flight jobs pin, not merely count them.** Today it refuses on any non-zero count: `CHECKOUT_ADVANCE_REFUSED n job(s) in flight, each pinning a commit`. That is a blunt probe — "pinning a commit" is not "pinning *this* checkout". Its only bypass, `--override-reason`, is documented for one shape (*restoring* a pin) and skips the queue check **entirely**, so spending it here would buy the advance by disabling the check rather than by satisfying it. **The correct fix is to compare `HFRepositoryCommit` against the checkout's own HEAD and refuse only on jobs that pin it.** Its test case is already measured and recorded: on 2026-08-17 every in-flight job pinned the separate `systematics_deploy` at `72ca4e39` and **zero** pinned the checkout's `43e35be8`, yet the guard refused — correctly under its current rule, unnecessarily under the right one. **Post-consolidation tooling; the 2026-08-17 advance waited for the drain instead, and needed no override.** |
| 11 | **The chain watchers are NOT relaunched, deliberately.** The merge runs closure itself for all three tunes with a *stronger* invocation than the chain's (`expected_central_events=100000000` vs the chain's `-1`), and relaunching watchers would recreate the closure/merge CPU contention that is the documented cause of the band MISS. Next session: verify the merge's own closure reports, then run `tune_extract.sh` per tune |

### 8 — the pair-level unresolved-origin systematic, scoped

**Why it exists: M7 does not bound the observable** (review finding A2). M7 is
inclusive-level; the observable is a directed, conditional, multiplicity-binned
OS−SS yield after the full trigger/associate selection. A global rate cannot
bound a multiplicity-localized effect.

**Deliberately subset-scoped**, so it is a session and not a campaign:

| | |
|---|---|
| **scale** | **100 files per tune**, not 1000 — this is a systematic, not a central value |
| **method** | vary the tie-break for duplicate hard-carrier claims: production **demotes to unresolved**; the variation admits a **permissive tie-break** and re-measures |
| **binning** | **multiplicity-binned**, because that is the axis on which the effect can localize and the whole point is that an integrated number cannot see it |
| **selection** | the **complete production trigger/associate selection** — direct-primary, central ground state, trigger hard ancestry, acceptance, pairing, OS−SS |
| **uncertainty** | **block SEMs** over the ten canonical blocks, as everywhere else |
| **reported as** | the shift in the OS−SS yield per multiplicity bin, per tune |

**The pre-registration is written before the run**, as with M7 and Σ_b.

---

## WRITTEN — UNRUN — AVAILABLE

**A category of its own.** These are measurements that exist as code and have no
recorded run. **None is dead, none is planned**, and any can be run if a question
makes it worth doing. `docs/VALIDATION_INVENTORY.md` is the full inventory.

| macro | bears on |
|---|---|
| ~~`Validation/CalibrateMultiplicityAgainstMinBias.C`~~ | **C8** — per-tune percentile offsets. ⚠ **NOT unrun — this entry is wrong.** It ran 2026-08-09 for all three tunes in both arms (`B4_RUN_EXIT=0` × 6) from `/data/alice/ipardoza/b4_mapping/`, producing the **51.201** / **12.948** counters `NCH_DECAY_POLICY_BIAS_8317.md` quotes. Found by the 2026-08-17 scratch reconciliation; struck through rather than deleted because other sessions have read this table. `docs/SCRATCH_RECONCILIATION.md` §4.3 |
| `Validation/TestPrimaryChargedDefinition.C` | **C8**, generator-side counterpart |
| `Validation/TestInclusiveRawKinematics.C` | **B3** — the blocked inclusive-spectra path |
| `Validation/AuditTuneSettings.C` | tune-settings audit |
| `Validation/TestHardCarrierUniqueness.C` | hard-carrier uniqueness |
| `Validation/TestPlotProjectionCuts.C` | plotting projection cuts |

> **This is the same shape as M7**, which sat unrun until the review asked, then
> took one session to become a table with an uncertainty. Listing them keeps the
> choice visible rather than accidental.

---

## PERMANENTLY NOT REGENERABLE — the second category, closed

README's contract is that every published number is **either regenerable from
committed inputs, or recorded as not regenerable with the reason. There is no
third category.** This is the second category, recorded so it is a closed known
rather than something rediscovered later.

### Every figure in `plotting/PAPER_FIGURE_PROVENANCE.md`

**Its input dataset no longer exists.** The v2 plotting configuration points at
`AnalyzedData/complete_root_21_06_2026` and
`AnalyzedData/SUBSAMPLES_700/combined_root_subSamples`; **both are absent
locally and on Nikhef** (measured 2026-08-13, `docs/PLOTTING_V3_DELTA.md` §2b).

**No test and no recipe in this repository can reproduce those figures**, and
none should claim to. The v2 configuration survives as a readable record of what
was done — the parameters, the selection, the class definition — but it is a
description, not a recipe.

**Consequence, and it is the reason this is recorded rather than noted:** any
argument of the form "keep this code path so the old figures stay regenerable"
is void. It cost one owner ruling already — B6 was first ruled to preserve the
per-tune multiplicity derivation on exactly that basis, and was revised to
replacement once the data was found to be gone.

---

## NOT PLANNED — deliberate, so nobody re-opens them

- ~~**Systematics beyond M7.** PDF and scale variation are **not addressed**, and
  no systematic uncertainty is propagated anywhere in the analysis.~~
  > **NO LONGER TRUE — 2026-08-17. This item has left "NOT PLANNED".** A
  > six-source program is pre-registered in
  > [`docs/SYSTEMATICS_PREREGISTRATION.md`](docs/SYSTEMATICS_PREREGISTRATION.md);
  > results land in [`docs/SYSTEMATICS.md`](docs/SYSTEMATICS.md). **Scale (μ_R and
  > μ_F, varied independently), PDF and pTHat are LAUNCHED** — seven campaigns,
  > 2100 jobs, Condor `5519094`–`5519100`, from a separate deploy at `72ca4e39`;
  > the frozen checkout was not touched. **S5 (decay-daughter class migration) is
  > measured and is an exact zero.** **S6 (the A2 pair-level systematic) was
  > already done.** S4 (counter window) is pre-registered and deliberately **not**
  > launched until the checkout advance in PENDING #5.
  >
  > *Still true, and now the live constraint:* **no systematic uncertainty is
  > propagated into any published number yet**, and none may be until every
  > non-negligible source in a tune's column has a measured value.
- **A kinematic-differential unresolved systematic.** M7 is integrated over the
  full central acceptance; whether the unresolved rate varies with pT or
  multiplicity is unmeasured. **Superseded as a "not planned" item by the
  pending pair-level measurement below** — a differential rate is exactly what
  that measurement needs.
- **The tune-bundle confound.** JUNCTIONS re-tunes the parameters that set baryon
  production, so a MONASH-vs-JUNCTIONS difference in a baryon observable
  **cannot** be attributed to junction formation alone. Documented, not resolved.
- **The junction hang's mechanism.** Not reproducible: 1 M events on 8.315 with a
  byte-identical card and the exact seed of a job that hung did not hang. The
  remaining untested hypothesis is node dependence. **The discard rate is
  reported, never corrected away** — the hang hits dense-junction topologies,
  which are exactly the configurations under study.
- **A container or an automated PYTHIA build.**
- **The contention recurrence.** Pre-registered 2026-08-12, **superseded and
  never scored**: it predicted scheduling, not physics, and gated no number.
- **Infrastructure:** no LICENSE, no CI, no DOI.

---

## THE TWO OPEN QUESTIONS THAT ARE NOBODY'S TASK YET

| # | question |
|---|---|
| **Q1** | `docs/history/studies/Balancing_and_Sampling/ATTENTION.txt` records that double-counting is *not* implemented from 23 December onwards, that results "will have to be divided by 2 manually", and ends *"remains to be checked"*. **Nothing in the tree says it was checked.** Does it affect anything published? |
| **Q2** | **Are the paper figures digest-pinned anywhere?** `plotting/PAPER_FIGURE_PROVENANCE.md` exists; whether any figure *output* carries a recorded digest was not established. If not, the freeze contract has a hole on the figure side |
