# A2 — the pair-level unresolved systematic: RUN RECORD

**Pre-registration:** `docs/A2_PAIR_UNRESOLVED_PREREGISTRATION.md`, committed
`6a56572`, before the variation was built and before any job was submitted.

> ## STATUS 2026-08-13: MEASURED, ON BOTH TIE-BREAK DIRECTIONS
>
> The pre-registered **smallest-`heavyIndex`** arm ran (campaign `5486752`) and
> is scored verbatim in `docs/a2_results_20260813/A2_DELTA_RESULT.md`. The
> **largest-`heavyIndex`** robustness arm ran the same day (variation
> `4e491134…`, regression `5489016` **PASS**, campaign `5489612`, 300/300
> promoted, zero held, 13 minutes) and is in
> `docs/a2_results_20260813/A2_TIEBREAK_ROBUSTNESS.md`.
>
> **The shape is robust and the magnitude is not.** Both rules rise **5.9–9.7×**
> across the multiplicity classes — that robustness is the headline, and it is
> what makes per-class quoting mandatory rather than stylistic. The largest-index
> arm is 2.0–5.5× larger in every colour-reconnection class, at 2.7–21.6 σ.
>
> **Quote the LARGEST-index arm, per class** (owner ruling): JUNCTIONS 0.0255 →
> **0.1509** (M4), CLOSEPACKING 0.0377 → **0.2293** (M5), MONASH negligible. The
> smallest-index arm is the **cross-check that establishes rule dependence**, not
> a lower bound. Never the integrated value: it understates the worst class by
> 2.6–2.9×.
>
> **Not an envelope.** What is quoted is *the larger of two extremal orderings of
> `heavyIndex`*. **Neither ordering bounds the space of resolutions** — a
> pT-ordered rule would give more, which is why §3 rejected it as inflating the
> shift by construction.
>
> **A pre-registered assumption was falsified, and this is a METHOD FINDING
> rather than a scoring footnote.** §3 below chose the winner rule on the
> reasoned argument that `heavyIndex` is *"deliberately uncorrelated with pT"*.
> Both arms restore an **identical** number of rows, so the entire 2–5.5×
> difference is how often the winner survives the trigger selection:
> `heavyIndex` **is** correlated with it, and neither direction is the neutral
> one. The registered text stays unedited; the annotation in the
> pre-registration carries the correction.

---

## 1. THE KEY ENABLING FACT

**No re-generation is needed.** Origin resolution happens in the producer, which
suggests the campaign would have to be regenerated to vary it. It does not: the
producer snapshots `originalMatchedHard` *before*
`EnforceUniqueFinalHardCarrier` and writes it into `heavyRejectedHard{C,B}` for
exactly the demoted rows
(`generation/producer/heavyflavourcorrelations_status.cpp:1215-1239`).

**The raw record therefore states, per hadron, which hard quark it contested** —
precisely what a permissive tie-break needs. The measurement is a re-analysis of
existing raw files.

## 2. PROVENANCE

| | |
|---|---|
| baseline macro (frozen, production) | `a101a0a1084a1e0a369e8bd637c1aa982641db26ba3fafa8c70bc5093b620f00` |
| **variation macro** | `22120383b07eb3572660f9a2aa7c895dd260ee23c7bc349a5a2e4f76262256de` |
| production commit | `61fe978f66c00e8467f88c00d677462292dd5a1c` |
| scratch tree | `/data/alice/ipardoza/a2_variation` |
| patch generator | `/data/alice/ipardoza/a2_make_subs.py`, variation patch `patch_variation.py` |
| **regression cluster** | **`5478114`** (1 job, permissive OFF) |
| **permissive cluster** | **`5478127`** (300 jobs, permissive ON) |
| submit logs | `/data/alice/ipardoza/a2_{regression,permissive}_submit.log` |
| outputs | `/data/alice/ipardoza/a2_runs/{regression,permissive}/<TUNE>/slot_NNN` |
| slots | `slot_000`–`slot_099`, all three tunes = 300 jobs |
| baseline | the **committed** `per_job` outputs for the same slots — not re-run |

**Cluster ids are taken from the `condor_submit` output**, captured with `tee`
at submission, not recovered afterwards by `tail`.

> **Resource requests right-sized 2026-08-13.** The submit profile was inherited
> wholesale from the campaign file: **8 GB memory and 8 GB disk** against a job
> that, measured over 60 completed production runs of the same macro, peaks at **158 MB
> and runs ~47 s**. An 8 GB request only matches slots with 8 GB free. All 301 queued
> jobs were edited in place with `condor_qedit` to **1024 MB / 2 GB** — not a resubmit,
> so cluster ids, queue position and provenance are unchanged. **`JobCategory = "long"`
> was deliberately left alone**: it is plausibly also costing matches, but it maps to
> site policy and sits close to the accounting-group line. Owner call.

### The scratch tree was built from the production commit, not from HEAD

`git archive 61fe978f | tar -x` into `a2_variation`, then the variation macro
installed over `AnalysisScripts/status_analysis_THnSparse_qq.C`. **HEAD is
`43e35be8`, not the commit production used**, and building from HEAD would have
risked confounding the origin-rule change with unrelated drift. Verified
afterwards that the two commits are in fact identical across
`AnalysisScripts`, `SimulationScripts`, `Validation`, `run_status_analysis.sh`
and `setupEnv.sh` — so nothing was riding on it, which is only knowable because
it was checked.

**The frozen checkout was read and never written.** The M7b pattern.

### ⚠ THE COROLLARY, learned the expensive way — 2026-08-13

**`git archive` extracts no `.git`, so a tree deployed from a tracked commit
cannot be asked which commit it is.** All 301 jobs died on `ExitCode 128` at
`run_status_analysis.sh:60`, `git -C "${project_base}" rev-parse HEAD`, under
`set -euo pipefail`. The stderr was 143 bytes and said exactly this:
*"fatal: not a git repository (or any parent up to mount point /data)"*.

> **The rule and its corollary, together, are the standing rule:**
>
> 1. **Deploy from a tracked commit**, never from a dirty tree — unchanged.
> 2. **An archived tree carries its commit in the ENVIRONMENT, not in `.git`.**
>    Provenance there is **injected**, never discovered. The archive was *made
>    from* a tracked commit, which is the same guarantee the tracked-clean check
>    provides for a real checkout — but only the deployer knows it, so only the
>    deployer can state it.
>
> ### ✅ REFINEMENT — owner ruling, 2026-08-17. Which deploy shape to choose
>
> Rule 2 says what to do **once you have an archive**. It does not say when to
> make one, and the systematics deploy showed the choice is not free:
>
> 3. **A real clone when the target VERIFIES the commit; archive plus
>    environment injection when it merely RECORDS it.**
>
> The distinction is what the consumer does with the sha. A2's analysis wrapper
> **recorded** provenance, so an injected sha lost nothing. The production worker
> `generation/submit/runCondorJob.sh` **verifies**: it compares
> `git rev-parse HEAD` against the value the submit file committed to and refuses
> a tree with tracked modifications — and `HADRONIZATION_REPOSITORY_COMMIT` is on
> its forbidden-inherited list, so injection cannot even reach it. Deploying an
> archive there would have forced that guard down from a check to an assertion.
>
> So the seven systematics campaigns (2026-08-17) were deployed as a **git clone**
> from a bundle, and every existing guard kept working unmodified. Cost: a `.git`
> in the deploy. **Transfer by `git bundle`, not by cloning the remote checkout** —
> that checkout's `.git` is 23 GB of historical blobs, while a full bundle of the
> working branch is 56 MB.
>
> **Ask, before choosing: does anything downstream compare this sha against
> something else?** If yes, clone. If it only writes the sha into a record,
> archive.

The fix is `HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT`. Discovery stays the default
for a real checkout; a tree that is **neither** a checkout **nor** carries an
injected sha is a hard error, because an unknown provenance is never guessed.
The wrapper logs which path it took as
`A2_PROVENANCE_SOURCE source=… commit=…`.

`verify_analysis_checkout()` had the same dependency and now verifies what
remains verifiable in an archived tree — the macro checksum, which is the thing
that could actually change under a running job — and re-interrogates git only
when git is what supplied the sha.

**The submit files already carried the sha** as `ANALYSIS_COMMIT`, argument 7,
and the wrapper already compared its discovered value against it. Only the
*discovery* was impossible; the value was never in doubt. That is why the fix is
an environment injection and not a new provenance mechanism.

**The deployed wrapper was patched, not replaced.** Its sha256 was
`83cd415e…2e9d4b`, identical to `61fe978f:run_status_analysis.sh` and **not** to
the repository's current `analysis/run_status_analysis.sh` (`0e3d11bd…12e94d`),
which has drifted with the restructure. Overwriting it with HEAD's copy would
have reintroduced exactly the confound this section exists to prevent, so the
same anchored patch was applied to both, the deployed file's pre-patch sha was
asserted before writing, and the original is kept beside it as
`run_status_analysis.sh.pre_provenance_fix`.

## 3. THE VARIATION, AS BUILT

121 changed lines against the frozen macro, all of them gated on
`HF_A2_PERMISSIVE=1`. Each insertion is anchored on a verbatim string and the
patch **fails loudly** if an anchor is not found exactly once — a patch that
silently no-ops is how a "variation" becomes a re-run of the baseline.

1. `<cstdlib>` for `std::getenv` and integer `std::abs`.
2. `A2::RestoreOneClaimantPerHardIndex` — the pre-registered rule.
3. Four extra branch pointers and their `SetBranchAddress` calls
   (`heavyMatchResolution{C,B}`, `heavyRejectedHard{C,B}`). **The production
   event loop never read these**, though the contract validator does and the raw
   contract already required them.
4. The rule applied after size validation and **before any downstream use**, so
   the trigger loop, closure loop and pair loop all see one consistent origin
   assignment.
5. `A2_PERMISSIVE restored_charm=… restored_beauty=…` reported per job, and a
   **throw if nothing was restored** — a silent zero would make every measured
   shift trivially zero and look like a clean null.

> **An anchoring subtlety worth recording.** The declaration block appears
> **twice** in the macro — once in the raw-contract validator (bound with
> `tree->`) and once in the event loop (bound with `chain.`). The first patch
> attempt matched both and aborted. The anchor now pins the `chain.` site.

## 4. THE FOUR POSITIVE CHECKS — status

| # | check | status |
|---|---|---|
| 1 | **regression**: rule disabled reproduces a committed `per_job` output | **PASSED 2026-08-13** for variation `22120383…`: 300 files, 300 diffs, every one of them the single allowed `analysis_macro_sha256` field, **zero unexpected**. Re-run against `a4df31e6…` after the guard removal — see §6. **The gate is MECHANIZED**: `analysis/a2_block_shift.py` refuses to run without a PASS sentinel for the exact variation sha, produced only by `tools/a2_record_regression.py`, which performs the comparison itself and has no `--verdict` flag. Tested by `tests/test_a2_regression_gate.py` (5 refusal paths + a negative control) |
| 2 | the rule restores > 0 rows, reported per tune | **MEASURED, and the check MOVED — see §6.** MONASH 6.2, JUNCTIONS 1 219.4, CLOSEPACKING 1 228.7 per M events. The per-job `throw` is **removed**: at MONASH's rate zero was the modal job outcome and the throw was selecting on the outcome variable. Now asserted once at **campaign** level by `check_campaign_restoration()` |
| 3 | `sameHardConstituentPairs` must not fire | enforced by the unmodified production check; awaiting a run |
| 4 | scratch deploy, sha-pinned, frozen tree never written | **DONE** — verified above |

### On check 1 and byte-identity

The macro embeds `analysis_macro_sha256` from the environment
(`status_analysis_THnSparse_qq.C:1258`), and the runner derives it from the
macro file. **A modified macro therefore cannot be literally byte-identical to
the baseline**: that one string necessarily differs.

**The check is therefore: every object identical except
`analysis_macro_sha256`.** A single, named, explainable difference in a metadata
string — not a tolerance, and not a waiver. If anything else differs, the
regression has failed.

## 5. ANALYSIS TOOLING — written, unexercised on real output

- `analysis/a2_pair_yield.C` — multiplicity-binned pair yields from
  `hCorrelations` (axis 6 is the multiplicity). Emits
  `slot,pair_file,mclass,yield` and **deliberately does not know OS from SS**;
  that mapping comes from the signed registry on the Python side, so a
  mislabelled file cannot be silently absorbed into a difference.
- `analysis/a2_block_shift.py` — the join, the block ratios (formed **inside**
  each block), the SEMs (dof 9), and the pre-registered verdict applied
  mechanically. Fails closed if the two runs cover different slots or if a
  filename is missing from the registry.

**Neither has been run against real variation output.** They are syntax-checked
and CLI-checked only.

## 6. TO FINISH THIS MEASUREMENT

1. `condor_q 5478114 5478127` — wait for completion; `max_retries = 0` and
   `on_exit_hold` on non-zero exit, so held jobs mean a real failure to read.
2. **Regression first.** Compare `a2_runs/regression/MONASH/slot_000` against
   `per_job/MONASH/slot_000`, object by object, expecting exactly one difference
   (`analysis_macro_sha256`). **If it fails, stop and diagnose — nothing
   downstream is usable.**
3. Confirm `A2_PERMISSIVE restored_*` is non-zero in the job logs, per tune, and
   record the counts.
4. Run `a2_pair_yield.C` over baseline and permissive slot dirs per tune, then
   `a2_block_shift.py --baseline … --permissive … --tune …`.
5. Record the per-class shifts with SEMs and the mechanical verdict here, then
   update `STATE.md` and the M7 documents.

**If the regression FAILS:** `tools/a2_quarantine_outputs.py --apply` moves all
300 permissive slot directories into a dated quarantine tree with a manifest.
It **moves, never deletes** — they are the evidence for whatever went wrong — and
it **refuses to run if the regression passed**, since quarantining a valid
measurement is its own kind of damage.
