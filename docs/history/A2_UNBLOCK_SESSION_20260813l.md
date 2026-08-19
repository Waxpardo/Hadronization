# A2 unblocked, and what the permissive arm is showing — 2026-08-13 (twelfth session)

**Suite 41/41 → 42/42.** Wall clock 17:22–18:15 CEST. `stbc-i3` up 18 h 15 m,
load ~16. The merge is still alive; JUNCTIONS blocks still 4/10.

---

## 1. THE HEADLINE — the regression gate PASSES, and the permissive arm is NOT a null

### The gate

```
COMPARE_DONE files=300 diffs=300 missing=0
allowed differences (analysis_macro_sha256): 300
UNEXPECTED differences: 0
verdict=PASS
```

**With the permissive rule disabled, the variation macro reproduces the
committed baseline exactly.** All 300 differences are the one allowed field —
the macro's own sha256, which differs by construction. Pre-registration
criterion 1 is satisfied: the variation is the baseline plus a gated change, not
a re-implementation carrying drift. Sentinel at
`/data/alice/ipardoza/a2_runs/regression/regression_sentinel.json`.

### ⚠ The permissive arm, IN FLIGHT and partial

Counted from the job logs' own `A2_PERMISSIVE` line, not from the analyzer:

Measured at 18:15 CEST, on **equal samples** — 68 jobs, 6.8 M events, per tune:

| tune | jobs done | events | charm restored | beauty | **per M events** |
|---|---|---|---|---|---|
| MONASH | 68 | 6.8 M | 44 | 1 | **6.6** |
| JUNCTIONS | 68 | 6.8 M | 8 201 | 119 | **1 223.5** |
| CLOSEPACKING | 0 | — | — | — | — |

**JUNCTIONS restores 185× more unresolved pairs than MONASH.** The rate is
stable as the sample grows — JUNCTIONS read 1 227 per M events at 19 jobs and
1 223.5 at 68, MONASH unchanged at 6.6 — so this is not a small-sample artefact.

If it holds, A2's question — does the unresolved-origin treatment bias the *tune
comparison* — has a loud answer: the baseline rule discards ~1 220 pairs per
million events in JUNCTIONS against ~7 in MONASH, so it does **not** act
symmetrically on the tunes being compared.

**This is not yet the pre-registered result and must not be quoted as one.**
123 jobs are still idle and 43 running; CLOSEPACKING has produced nothing; and
Δ in the pre-registration is a *yield ratio from the gated analyzer*, not a
restoration count. **The analyzer was deliberately NOT run** — see the next
section for why running it now would produce a biased number.

---

## 2. ⚠ THE GUARD IS NOW BIASING THE THING IT PROTECTS

The variation refuses to promote a job that restored nothing:

```
A2_PERMISSIVE restored_charm=0 restored_beauty=0 events_touched=0 selected_events=100000
ONE_PASS_ANALYSIS_ERROR A2 permissive mode restored nothing -- a silent zero would
make every measured shift trivially zero and look like a clean null
```

That guard was right when it was written: it catches a patch that silently
no-opped. **The measurement has now falsified its premise.** At MONASH's
measured 6.6 restorations per million events, a 100 000-event job restores
**0.66 pairs on average**, so restoring exactly zero is the *modal* outcome —
roughly half of MONASH jobs. **30 MONASH jobs are held on this guard right now,
and their outputs never promote.**

> **The consequence is a selection effect pointing exactly the wrong way.** If
> the gated analyzer consumes promoted directories, the MONASH permissive sample
> keeps only the jobs that happened to restore something, and drops the modal
> zero. At JUNCTIONS' 1 227 per million (~123 pairs per job) the guard will
> essentially **never** fire. So the bias acts on **one arm of the comparison
> only** — the arm A2 exists to compare.

**Owner call, and it is not a code question but a design one.** The guard
conflates two things it cannot distinguish at this sample size: *"the patch did
not apply"* and *"the patch applied and the effect is genuinely rarer than one
per job."* The first is a defect; the second is the measurement. A per-job
guard cannot separate them; a **per-campaign** guard can — zero restorations
across all 300 jobs is still a defect, zero in one job is now expected data.

Nothing was changed. The held jobs are intact and their evidence is recorded.

---

## 3. THE FIX THAT UNBLOCKED IT

**Diagnosis confirmed at the invocation before anything was touched.**
`run_status_analysis.sh:60`, `git -C "${project_base}" rev-parse HEAD`, under
`set -euo pipefail`; the deployed tree has no `.git` and every file is dated
Aug 9 17:40, consistent with `git archive`. The whole stderr was 143 bytes.

**Evidence recorded first**, at
`/data/alice/ipardoza/a2_runs/held_evidence_20260813/` — all 301 job ads with
hold codes, the unique hold reason, and the stderr. Nothing was deleted.

**The fix is injection, not discovery.** `HADRONIZATION_DEPLOYED_ANALYSIS_COMMIT`
supplies the sha an archived tree cannot be asked for. Discovery stays the
default for a real checkout, and a tree that is **neither** a checkout **nor**
carries an injected sha is a hard error — an unknown provenance is never
guessed. The wrapper logs which path it took. `verify_analysis_checkout()` had
the same dependency and now verifies the macro checksum, which is what remains
verifiable in an archived tree and is the thing that could actually change under
a running job. The corollary is recorded in the standing rule in
`docs/A2_PAIR_UNRESOLVED_RUN_RECORD.md`.

**The submit files already carried the sha** as `ANALYSIS_COMMIT`, argument 7,
and the wrapper already compared its discovered value against it. Only the
discovery was impossible; the value was never in doubt. That is why this is an
environment injection and not a new mechanism.

**The deployed wrapper was patched, not replaced.** Its sha256 `83cd415e…`
matches `61fe978f:run_status_analysis.sh` and **not** the repository's current
`analysis/run_status_analysis.sh` (`0e3d11bd…`), which has drifted with the
restructure. Replacing it with HEAD's copy would have reintroduced exactly the
confound the deploy record exists to prevent. The same anchored patch was
applied to both; the deployed file's pre-patch sha was asserted before writing
and the original kept as `run_status_analysis.sh.pre_provenance_fix`.

**Verified on one job before the rest**, as instructed. Cluster 5478114 released
17:28, terminated 17:35 with return value 0, `PAIR_DIRECTORY_VALIDATION
errors=0 expected_files=300 found_root_files=300
analysis_commit=61fe978f66c00e8467f88c00d677462292dd5a1c`, `PROMOTED_ANALYSIS`.
Only then were the 300 released.

**`tests/test_analysis_commit_provenance.py`** — 9 checks over the three
branches, with a negative control asserting a real checkout still discovers from
git, so the others cannot pass vacuously. It caught two errors in its own first
draft.

> **A monitoring lesson worth keeping.** `condor_q <cluster>` returned **empty**
> for a cluster that still held 272 jobs, and the monitor read that as
> "finished". The filesystem said otherwise: 8 promoted directories, not 300.
> **An empty query is not evidence of completion** — it is evidence of an empty
> query, especially against a schedd carrying 88 000 jobs.

---

## 4. THE REALISED CLASS FRACTIONS (owner ruling, Task 2)

Emitted by the stack as `tunes[…].realised_class_fractions` and published in
`docs/PRODUCTION_SHAPE_DECISION.md` beside the translation table, with the
distinction stated: **the translation table records where the labels came from
(the MB anchor); this records what a reader actually gets.**

| class | N_ch | MB label | MONASH | JUNCTIONS |
|---|---|---|---|---|
| c1 | 0–2 | 11.803 % | 11.776 % | 10.479 % |
| c5 | 7–8 | 9.542 % | 10.837 % | 10.700 % |
| c7 | 11–13 | 8.416 % | 10.051 % | 10.822 % |
| c10 | 24–32 | 8.702 % | 6.764 % | 7.665 % |
| **c11** | **≥33** | **8.422 %** | **4.472 %** | **5.588 %** |

(Full eleven-class table in the ruling doc.) Both columns sum to exactly 1.0
over 100 M events, underflow and overflow exactly zero.

The ruling's reason is recorded as the reason: the campaign sits ~36 % below
minimum bias in ⟨N_ch⟩ (`Model.tex:126`), so MB-derived absolute boundaries
under-populate the high-activity classes. **The top classes are correspondingly
thinner — c11 carries about half the events its label implies — and that is
where OS−SS subtraction stability is most at risk.** Stated, tabulated, not
investigated further.

`classes[].target_fraction` was left named as it was, with a `policy` line
saying plainly that it is the MB **label width** and not a fitted target.

---

## 5. TASK 3 — not reached

JUNCTIONS is still at 4/10 blocks, so the one-line `PYTHIA_TUNES` addition would
not run. The ratio canvases were correctly not chased. The two-tune **central**
pass was run anyway, because the realised-fraction table needed both tunes — it
is where the JUNCTIONS column above comes from.

---

## Next session

1. **The guard question in §2 is the blocking item** for the A2 harvest. Until
   it is settled, the gated analyzer will read a sample biased in one arm.
2. Then the standing protocol: gated analyzer, score the pre-registration
   verbatim, largest-index robustness check only if Δ exceeds negligible.
3. JUNCTIONS blocks 4/10 → 10/10 unblocks the two-tune figure.
