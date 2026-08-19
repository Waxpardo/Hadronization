# Cleanup and production-readiness report

**Session:** 2026-08-03 · **From:** `c1bb0d9` · **To:** `996cbf6` · 12 commits
**Basis:** `REPO_AUDIT_c1bb0d9.md`, whose corrections are recorded below.

---

## 1. What was deleted

291 paths, exactly the set in `deletion_candidates.txt`, in two revertible
commits. Nothing classified UNSURE was touched.

| Commit | Group | Files |
|---|---|---|
| `4d65266` | 1–4: pre-campaign submit stack, gate-era leftovers, editor backups, misc | 27 |
| `d799ae3` | 5: generated plot artifacts under `**/Plots/` | 264 |

| | before | after |
|---|---|---|
| tracked files | 721 | **430** |
| tracked content | 99 MB | **87 MB** |
| checkout | 109 MB | **97 MB** |

Verification ran after each commit, not once at the end. Step 3's cross-file
grep found 42 hits for groups 1–4 and 280 for group 5; **every one was in
markdown or a `SaveAs()` write target**, and an explicit read-pattern sweep
(`TFile`, `Open(`, `Get(`, `.L`, `source`, `import`) over all 291 basenames
across every `.C/.h/.cpp/.py/.sh` returned nothing. No surviving code reads a
deleted file.

One procedural correction: the verification procedure I wrote in the audit says
step 7 runs "after deleting, BEFORE committing". That is wrong —
`render_production_submit.py:111-118` refuses a tree with tracked
modifications, and staged deletions qualify. Step 7 ran after each commit.

## 2. What was fixed

| # | Commit | Fix |
|---|---|---|
| 4 | `2c242ea` | `.gitignore` now covers `submit_*_smoke.sub` and `submit_*_retry*.sub`. **Verified by measurement on Nikhef**: all 9 submit files report `!!`, and `git status --porcelain` returns zero untracked-not-ignored entries. |
| 5.1 | `f999657` | `run_status_analysis.sh` wrote `raw_schema: hf_primary_ground_raw_v5` at `:220,:336`; every other site says v7 and `validate_analysis_outputs.py:405` requires it. Free to change — `find` over both data roots on Nikhef returned **zero** `analysis_job_metadata.json`. |
| 5.2 | `753f95d` | Restored `tools/merged_pair_provenance.py` byte-identical (sha `e6644f7a…`). See §4. |
| 5.3 | `8be14d8` | `build_canonical_manifest.py` now writes the ten `block_NN.jsonl` files. |
| 5.4 | `802f766` | Widened the v2 receipt (`output_bytes`, `validator_dependency_sha256`); retargeted `AuditOriginResolution.C` and `ListUnresolvedOrigins.C` to accept both schema versions and both field spellings. |
| 5.5 | `5914892` | Six Python sites now import `campaign.PUBLISHED_TUNES`. |
| 5.6 | `6fe9298` | `make_subsamples.sh` merge-shape claim; `README.md` list numbering. |
| 7 | `21ac1a4` | Documentation: contradicted claims, six code-only design decisions. |
| 8 | `43fe711`, `996cbf6` | `make check` on the cluster. See §5. |

## 3. What broke

Nothing. `make test` stayed 21/21 locally after every commit, `make cards`,
`cards-current` and `registry` passed throughout, and the three generated
`Generated*.h` headers are byte-identical to `c1bb0d9` — checked explicitly
after the 5.5 tune-list migration, because including `JUNCTIONS_MATCHED` there
would have changed the registry the producer embeds.

The rebuilt producer hashes to `e54b27bb9e3f…`, **identical to the binary the
HF_PT2 jobs ran against**, confirming nothing changed its translation unit.

## 4. Corrections to the audit and the handoff

The repository won four arguments this session.

1. **`statistical_robustness.py:603` is a reader, not a writer.** My audit
   finding F4 called it "the sole writer" of `block_NN.jsonl`, and the task
   brief inherited that. `:601-610` re-validates those files. **Nothing wrote
   them.** This made 5.3 easier, not harder — two consumers pin the format
   exactly, so it was recoverable rather than a guess.
2. **Both merge blockers the handoff predicted are already gone.**
   `kFirstStageSlots` does not exist (removed in `1f411cf`), and the `N>=100`
   floor was replaced by `>= 10 and % 10 == 0`
   (`validate_analysis_outputs.py:112-113`). HF_PT2 at 10 jobs/tune is exactly
   the minimum valid shape.
3. **Decoupling the merge from `merged_pair_provenance.py` would have been
   wrong.** The audit inferred it was "simply missed" in `984370a` — true of
   the cause, false of the remedy. Two of its three sidecars are required
   inputs to `PlottingScripts/Validate_THnSparse_Production.C:450-456,779,817`,
   which is live-reachable from `run_paper_plots.sh:618`. Decoupling would have
   moved the failure from rung 5 to rung 6 and discarded the checksum binding
   between merged output and the canonical manifest.
4. **The 2-bit tune ordinal never blocked anything.** Two bits hold four
   configurations; the study has four. The real barrier to `JUNCTIONS_MATCHED`
   is that `TuneOrdinal` (`HeavyFlavourUtils.h:396-401`) maps three tunes while
   the producer whitelist (`heavyflavourcorrelations_status.cpp:124`) has four
   — so such a job throws at its first event. Given the decision that
   JUNCTIONS_MATCHED stays out of production, that throw is a **fail-safe**,
   not a defect. Documented, not changed.

## 5. `make check` on the cluster

`make check` could not pass on Nikhef in any environment, since the C++20
migration in `a6adab748`. Two mutually exclusive failure modes:

- **bare shell** — 16/21. Five tests raise `RuntimeError: ROOT is required`
  rather than skipping.
- **with ROOT** — 20/21. `test_validate_raw_output_strict_compile.py` pinned
  `-std=c++17` (`:15`) and stripped ROOT's own `-std=` (`:33`), so ROOT's
  C++20-mismatch `#warning` became an error under `-Werror`. It was failing on
  a ROOT header, not on `ValidateRawOutput.C`.

`43fe711` takes the standard from `root-config`, keeping every warning flag.
**Result: 21/21 on Nikhef with `source ./setupEnv.sh && make check`.**

I also tried sourcing `setupEnv.sh` inside the test recipe. It does not take
effect on the child processes — verified, `command -v root` inside the recipe
returns empty while the identical source in the calling shell works. `996cbf6`
reverts that and documents the requirement instead, rather than shipping a line
that looks like it solves the problem.

**Correction to an earlier reading in this report's own history.** I first
attributed the laptop/cluster divergence to the ROOT-dependent tests *skipping*
off-cluster. That was wrong: the laptop has ROOT too (homebrew 6.38.04). The
real cause is that the two ROOTs are configured for different C++ standards --
laptop `-std=c++17`, Nikhef CVMFS `-std=c++20` -- and the test hardcoded
`c++17`, which matched one and mismatched the other. Taking the standard from
`root-config` is correct on both.

**The trap that remains:** the five ROOT-dependent tests fail rather than skip
when ROOT is genuinely absent, so a count alone does not tell you whether a run
was meaningful. `tools/run_tests.sh` now prints the resolved `root` path, or
says explicitly that a run without it is not a green run.

## 6. Phase 8 readiness ladder — where I actually got to

| Rung | State | Evidence |
|---|---|---|
| 1. `make check` green | **GREEN**, conditionally | 21/21 on Nikhef *with `setupEnv.sh` sourced*; 16/21 bare. Documented, not hidden. |
| 2. `make build` clean, 0 warnings | **GREEN** | `PRODUCER_BUILD_READY sha256=e54b27bb…`, no warnings. |
| 3. `make manifest` incl. ten blocks | **GREEN** | Real HF_PT2 data: 30 rows, `block_01..10` × 3 rows each. |
| 4. analysis runs and promotes | **PARTIAL** | `ANALYSIS_DRY_RUN_OK`; `CANONICAL_RAW_VALIDATION errors=0 files=30 unique_seeds=30 total_events=3000000`; 30-row submit rendered. **Jobs not yet run, so `ValidatePairDirectory.C` has not promoted anything and the empty-provenance prediction is UNTESTED.** |
| 5. `merge_root_files.sh` completes | **NOT REACHED** | Blocked on rung 4. |
| 6. `run_paper_plots.sh` produces figures | **NOT REACHED** | Blocked on rung 5. |

**The pipeline is not ready for the full campaign.** Rungs 4–6 have never run
in this repository's history and still have not. Three merge blockers were
fixed this session; none is verified against real data. That is the actual
risk, and it is unchanged in kind — only in count.

## 7. What I skipped, and why

- **296 UNSURE files** — Q1–Q9 in audit §7 are unanswered.
- **`tools/statistical_robustness.py`, `tools/evaluate_pthat_sensitivity.py`** —
  out of scope. Note a raw-schema bump would be unable to avoid the first.
- **`REPOSITORY_FILE_CATALOG.md`, `README.txt`, `plotting_documentation.md`** —
  Q8. All three still carry stale references, including `raw_v5`.
- **Phase 6 code** — no code by decision.
- **`tests/test_submit_rendering.py:103`, `tests/test_plot_dataset_integration.py:15`** —
  left spelling the tune triple out. A test that imports its expected value
  from the code under test stops testing anything.
- **Non-Python tune sites** — `PlottingScripts/TunePlotStyle.h:13`,
  `Validate_THnSparse_Production.C:44`,
  `Plot_InclusiveKinematicSpectra_Raw.C:789,1953`,
  `merge_root_files.sh:186,202`. A single source would need either a generated
  header (the mechanism `generate_registry_artifacts.py` already uses) or
  reading the tune list from config at runtime. Reported, not improvised.
- **`freeze_summary.json`** — `statistical_robustness.py:438` reads it for a
  `block_manifest_sha256` map; nothing writes it. Same class of gap as the
  block files, out of scope this session.
