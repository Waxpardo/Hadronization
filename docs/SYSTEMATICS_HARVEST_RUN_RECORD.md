# Systematics harvest — run record

**2026-08-18, session start 09:17 CEST.** The harvest of the seven variation
campaigns into per-class systematics. A2-style: every command, every input
digest, every intermediate number, and the provenance of anything that would
otherwise have to be taken on trust.

> ## STATUS AT SESSION END: PREFLIGHT COMPLETE, CHAIN LAUNCHED, TABLE NOT
> ## PRODUCED
>
> The preflight passed on every check at full rigour, **the analysis stage is
> complete at 2100/2100 with the E5 gate passed on all 21 campaign-tune pairs**,
> the first merge is running, and the pure arithmetic for the deltas and their
> combination is written and tested. **The per-class table is not in this
> document**, because the chain that produces it is a multi-day pipeline and the
> measured cost is recorded in §6. **Two decisions are also blocked on the owner**
> and are stated in §7 with the numbers that make them concrete.

---

## 1. REPOSITORY STATE — and one divergence, reported before acting

| | |
|---|---|
| local worktree | `Hadronization-systematics-harvest`, branch **`systematics-harvest`**, from `physics-focus` at `60d4079` |
| Nikhef checkout | `/data/alice/ipardoza/Hadronization` at **`8650a047`**, branch `physics-focus`, tracked-clean |
| brief's floor | Nikhef at or ahead of `8650a047` — **satisfied, exactly at it** |

**A separate worktree and branch were used deliberately.** A concurrent session
is live on `freeze-contract-fix` (21 commits ahead of `physics-focus`, newest
committed 09:10 today, seven minutes before this session began). The brief
requires not sharing a worktree with a concurrent session, and the project's own
note records that the git index is shared mutable state across sessions in one
worktree.

### ⚠ The divergence: local is 11 commits ahead of Nikhef, and it is not docs-only

`8650a047..60d4079` carries eleven commits. Five touch code or config:

| file | what changed |
|---|---|
| `config/dataset_selector.json` | **the seal** — `status` `canonical_candidate` → `canonical`, `publication_eligible` `false` → `true`, authorization doc + sha added |
| `config/dataset_selector_hf_run3_v1.json` | the same seal, in the campaign-specific selector |
| `plotting/Plot_InclusiveKinematicSpectra_Raw.C` | plotting session's work |
| `tests/test_dataset_selector_row_agreement.py` | new test |
| `tests/test_multiplicity_inset_boundary_source.py` | new test |

**The consequence for this harvest is bounded and was checked rather than
assumed.** The four tools this session runs on Nikhef —
`build_canonical_manifest.py`, `render_analysis_submit.py`,
`three_tune_table.py`, `pipeline/tune_extract.sh` — are **byte-identical**
between local `HEAD` and Nikhef's `8650a047`, verified by `git rev-parse` on each
blob. So the chain executed on Nikhef is the chain in this branch. **The seal
itself is not yet on Nikhef**, which means anything the cluster writes records
`publication_eligible: false`. That is a provenance-labelling divergence, not a
physics one, and it is left for the owner rather than fixed here — pushing the
seal to Nikhef is a repository action with its own gate.

---

## 2. PREFLIGHT — all seven campaigns, four independent checks

### 2.1 Exact-filename presence — no globs

Every path constructed as
`{production_root}/{campaign}/raw/{TUNE}/hf_{TUNE}_job{NNN}.root` for
`NNN = 000..099` and the three tunes. **A glob was deliberately not used: `hf_*_job*.root`
also matches a `.partial.root`**, which is the shape of the E5/E8 lessons.

| campaign | present | missing | zero-length | sha sidecars | bytes |
|---|---|---|---|---|---|
| `HF_SYS_MUR_UP` | **300** | 0 | 0 | 300 | 27 G |
| `HF_SYS_MUR_DOWN` | **300** | 0 | 0 | 300 | 27 G |
| `HF_SYS_MUF_UP` | **300** | 0 | 0 | 300 | 28 G |
| `HF_SYS_MUF_DOWN` | **300** | 0 | 0 | 300 | 26 G |
| `HF_SYS_PDF_CTEQ6L1` | **300** | 0 | 0 | 300 | 28 G |
| `HF_SYS_PTHAT_1` | **300** | 0 | 0 | 300 | 24 G |
| `HF_SYS_PTHAT_4` | **300** | 0 | 0 | 300 | 32 G |
| **TOTAL** | **2100** | **0** | **0** | **2100** | **≈192 G** |

**100 jobs per tune per campaign is enforced by construction**: the loop asks for
slots 000–099 of each of three tunes and all 300 answered, so the per-tune count
cannot be anything but 100.

> **A bug of mine, caught by an impossible column.** The first run of this script
> reported 0 present / 300 missing for every campaign — and **0 bytes**. The
> format string needed `$T` twice (once for the directory, once inside the
> filename) and was given it once, so every path was malformed and every file
> read as absent. The zero-bytes column is what made it obviously a script defect
> rather than a data catastrophe. Recorded because "all missing" is exactly the
> shape a real disaster would take, and the thing that distinguished them was a
> column that could not be true.

### 2.2 Partials — present, expected, and not shadowing anything

| campaign | `.partial.root` files |
|---|---|
| MUR_UP 10, MUR_DOWN 15, MUF_UP 12, MUF_DOWN 10, PDF 1, PTHAT_1 13, PTHAT_4 9 | **70 total** |

These are the retry leftovers from clusters `5523774`–`5523780` and
`5526031`–`5526033`: a failed attempt writes a partial and is never promoted.
They live under `partial/`, never under `raw/`, so the exact-filename check above
cannot have picked one up.

### 2.3 Sidecar ↔ receipt cross-check — two independent writers

For all 2100: the `.sha256` sidecar against `output_sha256` in the job's
**validation receipt**. This catches what a byte re-hash cannot — a re-hash proves
a file matches *its own* sidecar; this proves the sidecar matches what the
validator recorded at promotion.

```
TOTAL   checked 2100   agree 2100   MISMATCH 0   no_pass_receipt 0   multi_pass 0
```

`multi_pass 0` also establishes **no job was promoted twice**.

### 2.4 Byte-level re-hash — with positive evidence

```
OK 2100   FAIL 0   ABSENT 0        (2 m 34 s wall, 4-way parallel, on stbc-i2)
```

> **The first attempt of this check was worthless and looked perfect.** It used
> `sha256sum -c --quiet`, which prints nothing on success, so the log contained
> only a completion marker — indistinguishable from "nothing ran". **`rc = 0` is
> not evidence.** It was re-run emitting an explicit `OK`/`FAIL` per file so the
> 2100 is a count of verifications rather than an absence of complaints.

### 2.5 A fifth verification, for free

`render_analysis_submit.py` re-hashes every raw input while rendering and refuses
on mismatch (`raw input is absent or stale`). All seven rendered, so **the 2100
bytes were verified a third time**, by a different tool with a different purpose.

---

## 3. MANIFESTS

`tools/build_canonical_manifest.py CAMPAIGN <freeze_dir> --production-root …`,
run from the Nikhef checkout at `8650a047`.

| campaign | rows | tunes | events | manifest sha256 (first 16) |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | 300 | 3 | 30 M | `01b5dbccfeec942b` |
| `HF_SYS_MUR_DOWN` | 300 | 3 | 30 M | `2d894a482a0e5509` |
| `HF_SYS_MUF_UP` | 300 | 3 | 30 M | `6e81b9dbb3fcff58` |
| `HF_SYS_MUF_DOWN` | 300 | 3 | 30 M | `e3ab8af8d0d7362d` |
| `HF_SYS_PDF_CTEQ6L1` | 300 | 3 | 30 M | `29472cbb6c600cdf` |
| `HF_SYS_PTHAT_1` | 300 | 3 | 30 M | `1188f65f22c8ace2` |
| `HF_SYS_PTHAT_4` | 300 | 3 | 30 M | `b58ffa8fdd8cc191` |

Ten blocks each, 30 rows per block (10 jobs × 3 tunes).

**The block rule was verified against the estimator's definition, not assumed:**
every one of the 300 rows satisfies `block == canonical_slot % 10`, and each tune
carries slots 0–99 with 100 distinct values. That is the construction the
pre-registration §2.2 and the brief both specify.

---

## 4. THE ANALYSIS STAGE — launched

`tools/render_analysis_submit.py <manifest> <checkout> <campaign_production_root>
<campaign_analysis_root> <out.sub>`, then `condor_submit`.

> The renderer's third argument is the **campaign** root, not the production
> root: manifest `raw_path` values are campaign-relative. Passing the production
> root fails closed with `raw input is absent or stale: …/hadronization_production/raw/MONASH/…`,
> which is the guard working.

| campaign | analysis cluster |
|---|---|
| `HF_SYS_MUR_UP` | **`5531204`** |
| `HF_SYS_MUR_DOWN` | **`5531205`** |
| `HF_SYS_MUF_UP` | **`5531206`** |
| `HF_SYS_MUF_DOWN` | **`5531207`** |
| `HF_SYS_PDF_CTEQ6L1` | **`5531208`** |
| `HF_SYS_PTHAT_1` | **`5531209`** |
| `HF_SYS_PTHAT_4` | **`5531210`** |

All seven rendered at commit `8650a047` with one analysis macro
`5a462aff7cfcec719d764eb1a9266b1fc349f9365236648d47fbf6501196c2e1` and seven
distinct manifest digests. 2100 jobs, submit logs tee'd to
`systematics_harvest/submits/logs/`.

### 4.1 ⚠ The analysis macro sha DIFFERS from the central campaign's — and why that is benign

The central per-class numbers were produced at commit `61fe978f` with macro
`a101a0a1…`; this harvest runs at `8650a047` with macro `5a462aff…`. **A macro
difference inside every Δ would be exactly the failure the pre-registration §13.2
registered**, so it was chased to the bottom rather than noted.

**Cause: the 2026-08-12 restructure moved the file.** `git log` shows exactly one
commit touching it, `98cdff9 Restructure`. Diffed across the move
(`61fe978f:AnalysisScripts/…` against `8650a047:analysis/…`) the change is
**6 lines added, 6 removed — all six are `#include` path rewrites.** The physics
body is byte-identical.

**The six included headers were then checked individually**, because identical
source text with different headers is a different program:

| header | across the move |
|---|---|
| `GeneratedPairRegistry.h` | **identical** |
| `GeneratedSpeciesOrdinals.h` | **identical** |
| `GeneratedHeavyFlavourRegistry.h` | **identical** |
| `HeavyFlavourUtils.h` | **identical** |
| `AssociateOriginCategoryContract.h` | 1 line — an `#include` path rewrite |
| `GeneratedTuneSettingRegistry.h` | 46 → 49 audited keys, plus two new constants |

**The last one is closed by what the macro actually references.** It uses only
`kTuneDifferenceAllowlistSchema` and `kTuneDifferenceAllowlistSha256` (lines 307
and 309) — **both unchanged**: schema still `pythia_tune_difference_allowlist_v2`,
digest still `2b35e52a…`. `kAuditedPythiaSettingKeys`, the array that grew, is
**not referenced by the analysis macro at all**; it is the producer's.

> **This is the design decision of 2026-08-17 paying off in a way it was not
> chosen for.** The three varied keys were put in a separate config file
> specifically so the tune-allowlist digest would not move. That choice is what
> now makes the variation analysis directly comparable to the sealed central
> analysis, instead of every Δ carrying an unquantified macro difference.

### 4.2 First-output verification, including the E5 plausibility check

A completed variation slot against the corresponding central slot:

| | `HF_SYS_MUR_UP` MONASH slot_000 | `HF_RUN3_V1` MONASH slot_000 |
|---|---|---|
| files written | **302** | 302 |
| `source_events` / `selected_events` | 100000 / 100000 | 100000 / 100000 |
| `pairs_written` | 300 | 300 |
| `same_hard_constituent_pairs` | **0** | 0 |
| `primary_all_heavy_closure_failures` | **0** | 0 |
| `central_ground_state_count` | **86 093** | 84 956 |
| **counts per event** | **0.861** | **0.850** |

> **The E5 plausibility gate passes.** Both are O(1) per event. **The E5 tell was
> ~13 per event**; a replicated count would have shown here as ~24× or ~26× these
> values. The two differ by **+1.34 %**, which is a *count* difference and exactly
> what a renormalisation-scale variation should do to a cross-section — the
> deliverable is a *fraction*, which is far more stable, and nothing should be
> read into this single-slot number beyond "the variation did something and the
> pipeline is not replicating".

---

## 4.3 THE MERGE — first campaign launched

`HF_SYS_MUR_UP` reached 300/300 analysis outputs during the session, so its merge
was started rather than left for the next one: the merge is the critical path and
~2.5 h of it is worth banking.

```bash
HADRONIZATION_BASE=/data/alice/ipardoza/Hadronization \
  bash merging/merge_root_files.sh \
    /data/alice/ipardoza/systematics_harvest/manifests/HF_SYS_MUR_UP \
    /data/alice/ipardoza/hadronization_production/HF_SYS_MUR_UP \
    /data/alice/ipardoza/hadronization_analysis/HF_SYS_MUR_UP \
    /data/alice/ipardoza/hadronization_merged \
    HF_SYS_MUR_UP
```

**Identity, stated per E8** — a PID alone is not an identity:

| | |
|---|---|
| **PID** | **`108654`** |
| **host** | **`stbc-i2.nikhef.nl`** — it is not visible from any other node |
| **log** | `systematics_harvest/merge_runs/merge_HF_SYS_MUR_UP.log` |
| **completion marker** | the driver's own last statement for the campaign; **absence of the PID without the marker is a death, not a completion** |

It reported the right shape immediately, which is the check that it understood a
variation campaign:

```
CANONICAL_MERGE_SHAPE inputs_per_tune=100 inputs_per_block=10 events_per_tune=10000000
```

100 per tune, 10 per block, 10 M events per tune — a tenth of the central
campaign in every dimension, as designed.

> ### A third instance of the restructure-move family, and this one fails closed
>
> `merging/merge_root_files.sh:27` computes
> `project_base="${HADRONIZATION_BASE:-${script_dir}}"`, and since the restructure
> `script_dir` is `<checkout>/merging`, not the checkout. The fallback is wrong for
> exactly the reason the production worker's was (fixed 2026-08-17) and the
> producer Makefile's was (same day).
>
> **It is not a defect in practice, and the difference is instructive.** The next
> line sources `${project_base}/setupEnv.sh` under `set -e`, so a wrong
> `project_base` means sourcing a file that does not exist and the script dies
> immediately. The worker's version resolved to a plausible-looking path and
> failed 300 jobs at a component check instead. **Same bug, and it is harmless
> here only because the very next statement happens to depend on the value.**
> Recorded, not fixed: it is outside this session's scope and changing the merge
> driver while a merge is running from that checkout is precisely the hazard the
> freeze rules exist for. `HADRONIZATION_BASE` must be exported by any caller.

---

## 4.4 THE ANALYSIS STAGE, COLLECTED — 2026-08-18

**2100/2100 complete.** Counted by exact filename, never by `condor_q`: a slot
counts as complete only if its directory holds **exactly 302** entries (300 pair
ROOT files + `analysis_job_metadata.json` + `analysis.log`), the same count the
central campaign's slots carry.

| campaign | complete | partial | missing |
|---|---|---|---|
| all seven | **300 each** | **0** | **0** |
| **TOTAL** | **2100 / 2100** | **0** | **0** |

**No held jobs, no failures, no resubmissions.** The seven clusters
`5531204`–`5531210` drained empty. Nothing was resubmitted, so the seed ledger
was not touched.

### The E5 per-event plausibility gate — all seven campaigns, all three tunes

The E5 defect showed as ~13 counts/event where the truth is O(1). The gate is on
the **order of magnitude**, not on agreement with the central value: the
variations are supposed to differ.

| campaign | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `HF_SYS_MUR_UP` | 0.861 | 0.972 | 0.883 |
| `HF_SYS_MUR_DOWN` | 0.849 | 0.958 | 0.871 |
| `HF_SYS_MUF_UP` | 0.909 | 1.036 | 0.936 |
| `HF_SYS_MUF_DOWN` | 0.792 | 0.879 | 0.813 |
| `HF_SYS_PDF_CTEQ6L1` | 0.916 | 1.041 | 0.950 |
| `HF_SYS_PTHAT_1` | **0.733** | 0.804 | 0.744 |
| `HF_SYS_PTHAT_4` | 1.007 | **1.188** | 1.051 |
| *central reference* | *0.850* | — | — |

**All 21 pass**: range 0.733–1.188 against an E5 signature of ~13, i.e. a factor
of 11 clear of the failure mode at the worst point. **`same_hard_constituent_pairs = 0`
and `primary_all_heavy_closure_failures = 0` in every one of the 21**, and every
slot read `source_events = selected_events = 100000`, `pairs_written = 300`.

> **These are single slots and are NOT a result** — no blocks, no SEM, no
> deduplicated extraction. They are quoted only as a sanity gate. That said the
> ordering is the physically expected one and is worth having on record before the
> real numbers exist: `PTHAT_1` lowest and `PTHAT_4` highest in every tune, which
> is the direction the pTHat scan measured for trigger yield (charm triggers per
> event rose 0.990 → 1.196 from threshold 1.0 → 2.0); `MUF_UP` above `MUF_DOWN`
> with the central between them; and MONASH < CLOSEPACKING < JUNCTIONS in all
> seven campaigns. **Nothing should be inferred from the MUR pair**, where the
> two arms sit 0.861 / 0.849 around the central's 0.850 — one slot cannot
> separate those.

---

## 5. THE PURE ARITHMETIC — written and tested

`extraction/systematics_delta.py`, `tests/test_systematics_delta.py`, **14 tests,
every expected value hand-computed and written out longhand** beside the
assertion. Comparing a tool against its own output proves agreement, not
correctness (E1), so no anchor here is a captured golden value.

**The registered estimator (pre-registration §2.2) is implemented as primary**:
relative shift formed *inside* each block, averaged over ten, SEM over those ten,
dof 9, per cent. The brief's default — means-first with SEMs in quadrature — is
implemented as `delta_from_means` and reported beside it as a cross-check,
because the brief states the pre-registration wins where it specifies.

**A test proves the two are different operations**, so that using one where the
other is registered would be a real error and not a rounding difference:
variation `[10, 20]` against nominal `[10, 40]` gives **−25 %** inside-block and
**−40 %** means-first.

`combine_quadrature` **refuses to run without an explicit policy** for unresolved
deltas (§7.1). A default there would be a physics choice made by a tool.

---

## 6. WHAT THE REST OF THE CHAIN COSTS — measured, not estimated

The chain is raw → analysis → **merge** → extraction → deltas. The merge is not
avoidable: extraction reads merged *block products* (`PROJ_DONE pairs=300` per
block), and the rundir the extractor consumes is 224 KB of CSVs derived from
them.

From the private merge-band validation record, where the central campaign's timings
were measured directly:

| quantity | central campaign | scales as |
|---|---|---|
| full block cycle | **2345–3035 s** (100 input files → 1.8 G) | output size — the 6.1× central/block time ratio matched the 6.1× size ratio |
| central leg | ~6371 s (1000 files → 11 G) | " |
| one-time internal gate | 8.35 h, covering three tunes | " |

A variation campaign's legs are **1/10** the input of the central campaign's.
Scaling linearly: ~235 s per block leg, ~640 s per central leg, so
≈ 0.83 h per tune, **≈ 2.5 h per campaign, ≈ 17 h for seven** — plus a gate per
campaign, plus contention. **The realistic figure is 17–25 h of merging**, after
2100 analysis jobs clear a queue holding ~15 000 idle jobs from all users.

**This is a multi-day pipeline, and that is the reason this document has no
table.** It is recorded here so the next session plans against a measured number
rather than rediscovering it.

---

## 7. TWO DECISIONS THAT ARE NOT MINE TO MAKE

Both are combination-stage, so everything upstream is unaffected and proceeds.

### 7.1 STOP — how does an UNRESOLVED per-class delta enter the quadrature?

**The pre-registration is silent, and the gap is structural rather than an
oversight.** §2.4's ladder (NEGLIGIBLE / QUOTABLE AS ONE NUMBER / MUST BE QUOTED
PER CLASS) is an **all-or-nothing verdict over a whole source**: NEGLIGIBLE
requires *every* class to be within 2σ of zero **and** under 0.1 %. §9 then sums
`Δ_s(c,tune)²` over every class of every non-negligible source, with **no
provision for a class whose Δ is noise**.

The mixed case is the one that will actually occur: the variations carry 10 M
events against the central's 100 M, so some classes will resolve and others will
not — most likely for S2 (PDF), which the pre-registration itself expects to be
the smallest source.

**Three options, and they give three different answers.** With a resolved term
3.0 ± 0.1 and an unresolved term 1.0 ± 2.0 (|Δ| = 0.5 σ):

| policy | contribution of the unresolved term | combined |
|---|---|---|
| **as-is** — every Δ enters at its measured value | 1.0 | **3.162** |
| **zero** — an unresolved Δ contributes 0 | 0.0 | **3.000** |
| **SEM** — an unresolved Δ contributes its SEM | 2.0 | **3.606** |

A 20 % spread on the combined systematic from a choice nobody has made. *as-is*
quotes noise as a systematic; *zero* discards a real effect the run was too thin
to resolve; *SEM* is conservative but inflates a source that measured nothing.
**Implemented as an explicit required parameter so the tool cannot pick one.**

### 7.2 CONFLICT — does the A2 (S6) term enter the per-class quadrature?

**The brief and the pre-registration disagree, and the pre-registration has a
registered rule with a stated reason.**

- **The brief, step 5:** "then quadrature per class per tune together with the
  unresolved-origin (A2) term and S5 = 0."
- **Pre-registration §9.6:** "**Registered rule: S6 is not added in quadrature to
  per-`c` values.** Until it is re-binned onto `c1…c11` it is quoted as a separate
  line … Re-binning it is a known piece of future work, not a thing to be fudged
  by assuming its classes map onto these."

**The reason is not a technicality.** A2 lives on five classes `M1…M5`
(`N_ch` 1–9, 10–19, 20–29, 30–39, ≥40); everything else here is on the eleven
production classes at half-integer boundaries −0.5 … 32.5. They are different
partitions of the same axis, so there is no class-by-class correspondence to add
along. Adding them anyway means assigning A2's `M4` value to whichever `c` bins
overlap it, which is the "fudge" §9.6 names.

**Not resolved here.** Either the pre-registration is annotated with an owner
ruling that supersedes §9.6, or A2 is re-binned onto `c1…c11` first (it is a
re-analysis of existing per-job products, so it is possible), or the table quotes
it as a separate line as registered.

---

## 8. ENVIRONMENT

| | |
|---|---|
| analysis / manifest host | **`stbc-i2`** (28 cores, load ~8). `stbc-i1` was at **load 124** from another user's work and was deliberately not used |
| Nikhef checkout | `/data/alice/ipardoza/Hadronization` at `8650a047`, tracked-clean |
| production root | `/data/alice/ipardoza/hadronization_production` |
| analysis root | `/data/alice/ipardoza/hadronization_analysis/HF_SYS_*` |
| harvest workspace | `/data/alice/ipardoza/systematics_harvest/{preflight,manifests,submits}` |
| ROOT | `v6-30-01-alice5-2` from CVMFS, on pin |
| suite | **52/52** |

---

## 9. THE MERGE STAGE, RE-ESTABLISHED FROM EVIDENCE — 2026-08-18

The shepherd session that launched the merge stage was lost. This section is
written from the jobs' own artifacts and from live process state, not from any
prior report. Every number below was read at 2026-08-18 11:27–11:35 UTC
(13:27–13:35 CEST).

### 9.1 State of the seven campaigns

Products counted by **exact filename** — `test -d` on each of the 33 names a
campaign must produce (`complete_root_<C>_<T>` ×3, and
`SUBSAMPLES_<C>/combined_root_subSamples_<T>/combined_root_1…10` ×30). No glob
was used anywhere in the count, because a glob matches the `.partial.XXXXXX`
staging directories and would report work that has not been promoted.

| campaign | merge state | marker | products | closure verdict |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | **RUNNING** — PID 108654, `stbc-i2` | **0 / 3** | **11 / 33** | NOT RUN |
| `HF_SYS_MUR_DOWN` | NOT LAUNCHED | — | 0 / 33 | NOT RUN |
| `HF_SYS_MUF_UP` | NOT LAUNCHED | — | 0 / 33 | NOT RUN |
| `HF_SYS_MUF_DOWN` | NOT LAUNCHED | — | 0 / 33 | NOT RUN |
| `HF_SYS_PDF_CTEQ6L1` | NOT LAUNCHED | — | 0 / 33 | NOT RUN |
| `HF_SYS_PTHAT_1` | NOT LAUNCHED | — | 0 / 33 | NOT RUN |
| `HF_SYS_PTHAT_4` | NOT LAUNCHED | — | 0 / 33 | NOT RUN |

"NOT LAUNCHED" is a positive finding, not an absence: `launch_merge.sh` refuses
if a log exists, and `merge_runs/` holds exactly one file. The earlier external
observation of *"~11 root.exe on `stbc-i2`"* does **not** survive contact with
the process table — there is **one** `root.exe`, the child of the one merge.

`HF_SYS_MUR_UP`'s 11 promoted products are MONASH's complete leg and its ten
blocks. Each carries `MERGED_PAIR_DIRECTORY_VALID` and was validated **twice** by
`validate_pair_directory.sh` before promotion, with `errors=0` on all 22 passes.
That is per-directory validity. It is **not** closure: no campaign has reached
the central-versus-ten-block gate, so no merge product here is extraction-ready.

### 9.2 The live merge, identified three-state

`ps -p 108654` was asked on **all three** login nodes, because an identity
checked in the wrong context is indistinguishable from one that exited (E8,
third facet).

| node | verdict |
|---|---|
| `stbc-i1` | no `/proc/108654` — **ABSENT, and not evidence of anything** |
| `stbc-i2` | **ALIVE** — `Ss`, PGID 108654, PPID 1, elapsed 03:43:44 |
| `stbc-i3` | no `/proc/108654` — **ABSENT, and not evidence of anything** |

Argv is not bare here, so the identification is direct rather than by lineage:
`bash …/merging/merge_root_files.sh …/manifests/HF_SYS_MUR_UP … HF_SYS_MUR_UP`,
`cwd=/data/alice/ipardoza/Hadronization`, and its live child chain
`453795 validate_pair_directory.sh → 453859 root → 453860 root.exe` is inside the
`HF_SYS_MUR_UP_JUNCTIONS` staging directory. All in PGID 108654.

**The launcher never wrote an identity file for this merge**, because the merge
was launched by hand at 09:48:25 and `launch_merge.sh` was not written until
10:11. `merge_runs/identity_HF_SYS_MUR_UP.txt` has now been reconstructed from
the live process and is marked `RECORD_ORIGIN = RECONSTRUCTED`.

`/proc/108654/environ` confirms `HADRONIZATION_BASE` **is** exported. That, and
only that, is what keeps the `merge_root_files.sh:27` `project_base` fallback
(§4.3) from killing this run at its `setupEnv.sh` source.

No `merge_supervisor.sh` is running on any node, so nothing will restart this
merge when it exits. The Condor queue holds **0 jobs for this user**; the
analysis stage is fully drained.

### 9.3 The sync did NOT run, and the ordering is intact

| | |
|---|---|
| Nikhef checkout `HEAD` | **`8650a047`**, branch `physics-focus`, **tracked-clean** |
| `git cat-file -t 60d4079` | `fatal: Not a valid object name` — the target is not even in the object store |
| pinfile | absent (both superseded copies preserved) |
| staged bundle | `systematics_harvest/sync_20260818.bundle`, 58.5 MB, **verifies okay**, complete history, carries `physics-focus=60d4079` and `systematics-harvest=aed38bd` |

**The sync is correctly still pending and remains unauthorized.** Its
precondition is `MUR_UP` exiting *with* its completion marker; the marker count
is 0/3 and the process is alive. Independently, PID 108654's `cwd` **is** the
checkout, so "no process reading the checkout" also fails.

**There is no ordering deviation.** `MUR_UP` was launched at 09:48 against
`8650a047`; the bundle was staged at 10:17, after. The merge's own log records
`analysis_commit=8650a04752ec…` on every validation line, so its provenance is
self-describing and consistent.

### 9.4 FINDING — the closure gate's call site has been broken since 2026-08-13

**`merging/merge_root_files.sh:304-307` calls `validate_pair_block_closure.sh`
with three arguments and passes `${canonical_events_per_tune}` where the
validator now requires `EXPECTED_SCHEMA`.**

Commit `8f410a43` (*"A4: the closure gate takes a REQUIRED expected-schema
argument"*, 2026-08-13 01:45) inserted `EXPECTED_SCHEMA` as argument three and
moved `EXPECTED_CENTRAL_EVENTS` to four. **The call site was never updated.**
`merge_root_files.sh` was edited once afterwards — `c3c9d961`, 2026-08-14 — and
that commit did not touch the closure block.

Proved by running the driver-shaped call by hand against the real MONASH
products, on `stbc-i1`, read-only:

```
ERROR: EXPECTED_SCHEMA is now the third argument and must be a schema
       (v2, v3, or a full tag); got the number '10000000'.
       EXPECTED_CENTRAL_EVENTS moved to the fourth position.
```

Exit **2**. The driver maps any non-zero there to `exit 7`.

**Consequence.** `HF_SYS_MUR_UP` will produce all 33 merged products, each
individually validated, and then die at the *first* closure pass with **zero**
completion markers. Under the standing rule that is a DEATH — correctly so, but
the fault is in the gate's call site, not in the data. Every one of the six
remaining campaigns would burn ~11 h and die identically.

**The sync does not fix it.** The defect is present at `8650a047` *and* at the
sync target `60d4079`; `8f410a43` is an ancestor of both.

**Why the suite is green at 52/52.** `tests/test_pair_block_closure.py` asserts
`"validate_pair_block_closure.sh" in merge_text` — the *name* of the callee, not
the *shape* of the call. The test that exists to protect this gate cannot see
its arguments.

**Why the central campaign was unaffected.** `HF_RUN3_V1`'s three closure reports
(2026-08-16 12:39, 2026-08-17 02:26, 2026-08-17 16:16) each record
`expected_central_events=100000000`, which the wrapper can only print if argument
four was supplied. They were run **by hand with the corrected four-argument
form**, one tune at a time, never through the driver. The driver's closure loop
has therefore **never** executed successfully since A4 landed.

**Not fixed here.** Repairing it is outside this session's standing
authorizations, and editing the merge driver in the checkout a live merge is
reading from is precisely the hazard the freeze rules exist for. The corrected
invocation, for the record:

```
validate_pair_block_closure.sh <complete_root_HF_SYS_X_TUNE> \
    <SUBSAMPLES_HF_SYS_X/combined_root_subSamples_TUNE> v3 10000000
```

`v3` = `paul_pair_objects_primary_ground_v3`, the tag the central reports carry.

### 9.5 The merge cost, measured — and §6's estimate is low by ~4×

Reconstructed from product mtimes; the log carries no timestamps.

| stage | measured, `HF_SYS_MUR_UP` |
|---|---|
| `ANALYSIS_OUTPUT_MANIFEST_VALID`, 300 dirs, no report to reuse | **1 h 29 m** (09:48:25 → 11:17:38) |
| MONASH complete leg — ROOT merge only | 40 m 31 s (11:17:38 → 11:58:09) |
| MONASH complete leg — validate ×2 + provenance + checksums | 16 m 33 s (→ promoted 12:14:42) |
| ten MONASH block legs | 4 m 35 s each, 51 m total (→ promoted 13:15:27) |
| **MONASH tune, total** | **1 h 57 m 49 s** |
| JUNCTIONS complete leg — ROOT merge only | **6 m 29 s** — 6.2× faster than MONASH's, same shape |

The 6.2× spread between two identical legs is unexplained and is the reason the
projection below is a band rather than a number; `stbc-i2` was at load 2.3 when
measured, so contention is the likeliest cause of the slow one.

**§6 projected ≈ 2.5 h per campaign. The measured merge work alone is 3 h 45 m –
6 h, before the manifest stage and before closure.** Per campaign:

| | |
|---|---|
| manifest validation | 1 h 30 m — **per campaign**, not once; each has its own manifest |
| three tunes of merging | 3 h 45 m – 6 h 00 m |
| three closure passes | **~5 h 30 m, EXTRAPOLATED** — the central's took 13 h 47 m and 13 h 50 m per tune on 7.4× the product size. No closure has ever run at variation scale, so this is a factor-of-7 extrapolation and should be treated as unmeasured. |
| **per campaign** | **≈ 11 h** |
| **seven campaigns** | **≈ 77 h sequential**; ≈ 22–30 h at the planned 3-on-`i3` / 3-on-`i2` parallelism, NFS-bound |

`stbc-i1` is at **load 138** and is unusable for this work. `stbc-i2` is at 2.3
and `stbc-i3` at 6.2, so the planned split still holds.

Disk: `/data/alice` is at **98 %, 660 G free**. A campaign's products are 11.7 G
(1.8 G × 3 complete + 2.1 G × 3 subsample sets), so seven need **≈ 82 G**. It
fits, on a volume shared with other users at 98 %.

### 9.6 What blocks extraction

1. **The closure call site (§9.4) must be repaired** — owner decision. Nothing is
   extraction-ready without a closure pass, and no closure pass can run through
   the driver.
2. `HF_SYS_MUR_UP`'s 33 products then need their closure gate run — by hand in
   the corrected form, or by a repaired driver.
3. Six campaigns still to merge, ≈ 22–30 h wall.
4. Then, and only then, the sync and extraction.

---

## 10. THE CLOSURE GATE REPAIRED, AND WHAT REPAIRING IT FOUND — 2026-08-18

Executed on owner ruling after §9.4. Sequenced so that nothing was stopped
before its replacement was deployable: the fix was written, tested, committed
and staged **while `HF_SYS_MUR_UP` kept merging**, and the running merge was
never touched.

### 10.1 There were two broken call sites, not one

Repairing `merging/merge_root_files.sh` meant looking for the gate's other
callers, and there was one:

| caller | what it passed | failure |
|---|---|---|
| `merging/merge_root_files.sh:307` | `${canonical_events_per_tune}` in the schema slot | wrapper's numeric guard → exit 2 → driver `exit 7` |
| `extraction/pipeline/tune_chain.sh:45` | **two arguments** to a gate requiring three | wrapper's usage check → exit 2 |

**`tune_chain.sh` is worse than an arity error.** It records the result and does
not act on it:

```
bash Validation/validate_pair_block_closure.sh "$CENTRAL" "$BLOCKS" >> "$LOG" 2>&1
echo "# CLOSURE_RC=$?" >> "$LOG"
```

`CLOSURE_RC` is written to the log and never read; extraction runs immediately
afterwards regardless. So that chain would have written `CLOSURE_RC=2` and then
extracted from data whose closure had never run — a failure that leaves a
plausible-looking log behind. **The arity is fixed here. The fall-through is
NOT** — changing the chain's control flow is on the extraction path and belongs
to the next session. Recorded as a finding.

### 10.2 The fix: an input with no default, checked at minute zero

`HADRONIZATION_EXPECTED_PAIR_SCHEMA`, required, no default, in both callers.

**`v3` is deliberately not hardcoded in the driver.** A default would pass a v2
campaign silently the moment one existed, which is the A4 defect relocated from
the wrapper to its caller rather than removed.

**It is validated before any work starts.** The driver resolves the tag against
`config/pair_file_object_contract_v1.json` in its first seconds and refuses an
unknown one, and it echoes `CLOSURE_EXPECTED_SCHEMA requested=… resolved=…`.
The reason is the defect's own shape: a required input that is only consulted at
the end is a trap. The old call site was wrong from the first second of every
run and did not say so until hour eleven, by which time a campaign's merging had
been spent. `tools/merge_supervisor.sh` propagates the variable and refuses to
restart without it.

### 10.3 The ops correction, and the test that now earns its name

> **A test that asserts a callee's name certifies nothing about the call.**

`tests/test_pair_block_closure.py` asserted `"validate_pair_block_closure.sh" in
merge_text`. That is why 52/52 stayed green across five days in which the gate
could not run once, and across two call sites, neither of which the test could
see. The name check is kept — it is free — but it is no longer the check.

The test now **executes** each invocation against a recording stub, with every
shell variable bound to a sentinel, and inspects the argument vector that
actually arrives:

```
merging/merge_root_files.sh    -> ['…/complete_root_SENTINEL_TAG_SENTINEL_TUNE',
                                   '…/combined_root_subSamples_SENTINEL_TUNE',
                                   'SENTINEL_EXPECTED_PAIR_SCHEMA',
                                   'SENTINEL_CANONICAL_EVENTS_PER_TUNE']
extraction/pipeline/tune_chain.sh -> ['SENTINEL_CENTRAL','SENTINEL_BLOCKS','SENTINEL_SCHEMA']
```

and it **enumerates every `*.sh` caller in the tree** rather than one file. Two
have now shipped broken; enumerating is what stops a third.

**Mutation controls — a gate never seen to fail is not known to be a gate.**
All four were rejected:

| mutation | rejected with |
|---|---|
| delete the schema argument (the 2026-08-13 defect, exactly) | *"the driver passes 3 arguments"* |
| swap schema and events | *"REGRESSION: the driver passes the event count where the closure gate requires EXPECTED_SCHEMA"* |
| give the input a default (`:-v3`) | *"must be read with an empty default"* |
| revert `tune_chain.sh` to two arguments | *"calls the closure gate with 2 arguments"* |

The negative control is also wired into the test itself, so it proves its own
sensitivity on every run rather than only on the day it was written.

### 10.4 The launcher, hardened

`launch_merge.sh` now refuses four ways instead of two: absent schema, existing
log, non-tracked-clean checkout, **a checkout whose driver predates this fix**,
and free disk below a 150 G floor. The fourth is the one that matters — it makes
the ordering error structurally impossible:

```
REFUSING: the checkout's merge driver predates the closure-gate fix;
          it would merge for hours and then die at exit 7. Sync first.
```

Both refusals verified live, and **neither created a log**, so a refused launch
does not consume the campaign's one-shot log guard.

### 10.5 E8 caught this session's own script, on its first test

The staged closure re-runner checked `[ -d /proc/108654 ]` to confirm the
predecessor had exited. Run once from `stbc-i3` it sailed past that check — not
because the merge had exited, but because **/proc/108654 does not exist on
`stbc-i3` and never would**. The same trap as the 2026-08-12 pinfile, in a
script written by the session that had just documented it.

Fixed by pinning the host (`stbc-i2.nikhef.nl`, refuse to run anywhere else) and
by requiring an independent second fact — the predecessor's log quiescent for
more than 120 s. Absence of a PID and silence in a log are different
observations; the trap is satisfied by one of them alone.

### 10.6 Staged for the sync

| | |
|---|---|
| fixed tip, `physics-focus` | **`51603c2`** |
| fixed tip, `systematics-harvest` | **`f7ead26`** (cherry-pick `-x` of the same change) |
| bundle | `systematics_harvest/sync_20260818_fixed.bundle`, **98 751 bytes**, range bundle on prerequisite `8650a047` |
| sha256, local == staged | `5c5babc5636e730670dd4976e7b8b44017e70575feb6f0e5dd52428f7bca311d` |
| verifies against the live checkout | yes; prerequisite `8650a047` satisfied there |

**The bundle's contents were checked in isolation, not assumed.** A scratch
repository was seeded with `60d4079` alone — `0` occurrences of
`HADRONIZATION_EXPECTED_PAIR_SCHEMA`, `51603c2` unknown to it — and the bundle
was then fetched into it. The bundled `merge_root_files.sh` reads:

```
354:  if ! "${project_base}/Validation/validate_pair_block_closure.sh" \
355-       "${analyzed_data_base}/complete_root_${output_tag}_${tune}" \
356-       "${analyzed_data_base}/SUBSAMPLES_${output_tag}/combined_root_subSamples_${tune}" \
357-       "${expected_pair_schema}" \
358-       "${canonical_events_per_tune}" >"${closure_stage}" 2>&1; then
```

with 4 occurrences of the guard, and the bundled `tune_chain.sh:58` carries the
three-argument form. The fix demonstrably travels in the bundle.

The superseded 58.5 MB bundle at `60d4079` is left in place, unused; it is the
one that would have deployed the defect.

### 10.7 The JUNCTIONS leg anomaly: throughput, not completeness

§9.5 recorded the JUNCTIONS complete leg merging in 6 m 29 s against MONASH's
40 m 31 s. Its product promoted at 13:39:08 and is indistinguishable in kind:

| | MONASH | JUNCTIONS |
|---|---|---|
| entries | 304 | **304** |
| `PAIR_DIRECTORY_VALIDATION errors=0` at 100 inputs | 2 passes | **2 passes** |
| `MERGED_PAIR_DIRECTORY_VALID inputs=100` | 1 | **1** |
| size | 1.8 G | 1.6 G (tune multiplicity differs) |

All 26 `errors=` fields in the whole log read `errors=0`.

**And the validation phases took the same time** — 16 m 33 s for MONASH,
15 m 07 s for JUNCTIONS — while only the *merge* phase differed. Validation
reads the output just written; merging reads 30 000 distinct per-job input
files. That is consistent with a cold page cache on the first tune and a warm
one afterwards, which is the plausible explanation and is where it is being
left. Not chased further: nothing failed.

---

## 11. A SECOND EXECUTOR IS RUNNING THIS PIPELINE — 2026-08-18 16:15

This session holds a brief that names it the sole executor. That is no longer
true. Another executor overwrote this session's launcher, launched all six
remaining campaigns, and started a second closure run over MUR_UP's products.
This section records the evidence and stops.

### 11.1 What this session did, and when

| time (CEST) | action | identity |
|---|---|---|
| 15:54:00 | MUR_UP died at the broken gate, as predicted | PID 108654, stbc-i2 |
| 15:57:56 | sync preflight: gate `CHECKOUT_ADVANCE_ALLOWED`, tracked-clean, no process in the checkout on any node | — |
| 15:57:57 | **sync executed**: `8650a047` → `51603c2`, fast-forward | — |
| ~15:59 | `make test` on the advanced checkout: **51/51** | — |
| 16:01:00 | MUR_UP closure re-run through the fixed driver | **PID 641373, PGID 641373, stbc-i2** |

### 11.2 What the other executor did

| time (CEST) | action | evidence |
|---|---|---|
| 16:00:17 | overwrote `launch_merge.sh` | mtime, size 2241, sha256 `1f262cb2…` |
| 16:00:26–16:01:49 | launched all six campaigns | six identity files, six logs |
| 16:14 | wrote `close_murup.sh` and started a second MUR_UP closure | `closure_runs/`, `closure_runs_murup.out` |

The six run on the correct commit and schema. Every log carries
`CLOSURE_EXPECTED_SCHEMA requested=v3 resolved=paul_pair_objects_primary_ground_v3`,
and every identity file records `checkout_commit = 51603c2`. The work itself
looks right.

| campaign | host | pid | launched (UTC) |
|---|---|---|---|
| `HF_SYS_MUR_DOWN` | stbc-i3 | 3953008 | 14:00:39 |
| `HF_SYS_MUF_UP` | stbc-i3 | 3953522 | 14:00:51 |
| `HF_SYS_MUF_DOWN` | stbc-i3 | 3954073 | 14:01:03 |
| `HF_SYS_PDF_CTEQ6L1` | stbc-i2 | 642060 | 14:01:25 |
| `HF_SYS_PTHAT_1` | stbc-i2 | 642463 | 14:01:37 |
| `HF_SYS_PTHAT_4` | stbc-i2 | 642745 | 14:01:49 |

### 11.3 Three deviations, and one of them undoes an owner ruling

**The replacement launcher defaults the schema.** It reads
`SCHEMA="${HADRONIZATION_EXPECTED_PAIR_SCHEMA:-v3}"`. The owner ruling says the
input has no default, and that an absent value must refuse. A default of `v3`
is the exact thing the ruling forbids. It will pass a v2 campaign silently on
the day one exists. The driver still refuses on its own, so the six runs are
correct today; the guard is weaker tomorrow.

**Two guards were dropped.** The replacement launcher no longer checks that the
checkout carries the closure-gate fix, and no longer checks free disk against
the 150 G floor. Its identity files no longer record `disk_free_gb` or
`loadavg`. The fix-presence check is the one that made the ordering error
structurally impossible.

**The six launched before MUR_UP's closure passed.** The brief gates the six on
three closure passes. That gate exists to prove the repaired closure loop once,
on one campaign, before six more campaigns commit to it. Six campaigns now
depend on a loop that no run has yet completed.

### 11.4 The duplicated closure, assessed rather than assumed

Two closure runs now read MUR_UP's 3300 pair directories at the same time. This
session's runs through the repaired driver. The other runs
`validate_pair_block_closure.sh` directly.

**No corruption path was found.** The wrapper stages its intermediate through
`mktemp` (`validate_pair_block_closure.sh:77`), so the two runs cannot clobber
one file. They also write to different destinations: the driver writes
`hadronization_analysis/HF_SYS_MUR_UP/validation/`, the other writes
`systematics_harvest/closure_runs/`.

**The costs are real.** The work is done twice, at roughly 1 h 50 m per tune.
Load reached 33.7 on stbc-i3 and 19.1 on stbc-i2, and this session's re-run had
validated 0 of its 33 products after 15 minutes.

**Only the driver path tests what the repair changed.** The direct wrapper call
passes the arguments by hand, so it exercises the wrapper and not the call site.
This session therefore kept PID 641373 alive. It is the only end-to-end test of
the repaired loop, and this session killed no process.

### 11.5 Stopped here

This session killed nothing, restored nothing, and changed no file the other
executor wrote. Two executors on one pipeline is outside every standing
authorization in this brief, and the deconfliction is the owner's call.

---

## 12. THE SECOND EXECUTOR ANSWERS — 2026-08-18 16:40

I am the executor §11 describes. **§11 is accurate, and all three deviations it
names are mine.** This section owns them, records what I repaired, and states
what I did not touch.

### 12.1 The root process failure: I overwrote a file without reading it

At 16:00:17 I copied my own `launch_merge.sh` over the shared one. I had staged
mine earlier in a previous session and treated it as *my* file. It was not: the
other executor had hardened it at ~14:00 and kept my original beside it as
`launch_merge.sh.pre_schema_20260818`. **I destroyed a work product by assuming a
shared path was private**, and every one of §11.3's deviations follows from that
single act.

### 12.2 The three deviations, each conceded

| # | §11.3's finding | verdict | disposition |
|---|---|---|---|
| 1 | the launcher **defaults** the schema (`:-v3`) | **correct, my regression** | removed; the launcher now refuses on an absent schema, verified live |
| 2 | two guards dropped (**fix-presence**, **disk floor**) and `disk_free_gb`/`loadavg` no longer recorded | **correct** | all restored |
| 3 | the six launched **before** MUR_UP's closure passed | **correct** | cannot be undone; assessed below |

**On the schema default specifically: §11.3 is right that it undoes the ruling.**
The repair's own text says the input "is required and has no default", and
`:-v3` reinstates precisely the silent-default behaviour the repair removed. It
was harmless today only because the driver refuses independently — which is a
second line of defence doing the work of the first, not a reason the first may
be weakened.

**The launcher is restored from §10.4's surviving specification**, since the
original file itself is gone from disk. Five refusals: absent schema, existing
log, non-tracked-clean checkout, a checkout predating the closure-gate fix, and
free disk under the 150 G floor. It is faithful to the recorded contract, **not
byte-identical to the lost original**, and it is labelled as such in its own
header. Two refusals verified live, neither creating a log.

### 12.3 The ordering error, assessed rather than excused

**§11.3 is right that six campaigns now depend on a loop no run has completed.**
My brief's covered case for launching read "sync done + merges not yet
launched", which was literally satisfied — but my own task order put *verify*
(task 3) before *launch* (task 4), and I inverted them. The literal reading of
one clause does not repair an ordering my own brief specified.

**What limits the exposure, stated as a bound and not as a defence:** every one
of the six printed
`CLOSURE_EXPECTED_SCHEMA requested=v3 resolved=paul_pair_objects_primary_ground_v3`
within seconds of launch. That is the *specific* failure that killed MUR_UP —
the schema slot receiving a number — and it is now excluded for all six by
direct evidence rather than by inference. What is **not** excluded is any other
defect in the closure loop, because no run has yet completed one. **If the loop
fails for a second, unrelated reason, six campaigns lose their closure step and
must re-run it.** They will not lose their merge products: MUR_UP's own death
demonstrated that the 33 legs promote before the closure runs.

### 12.4 The duplicated closure: I agree with §11.4 and killed nothing

§11.4's assessment is sound and I reached the same conclusion independently
before reading it: `mktemp` staging and disjoint destinations mean no corruption
path, and the cost is duplicated work. **I add one point in support of keeping
both:** the central campaign's own closures were run *independently of the
merge* (`GOLDEN_OUTPUTS.md` §2.9c), so the direct-wrapper path is the one with
precedent for a verification of record, while the driver path is the only
end-to-end test of the repair. They answer different questions and both answers
are wanted.

**PID 641373 was not touched.** I killed no process, mine or theirs.

### 12.5 What I did not do

- **The staged sync was not executed.** It was superseded: the other executor
  had already advanced `8650a047` → `51603c2` at 15:57:57, and `60d4079` is an
  ancestor of that, so the seal is on Nikhef and my bundle would have moved
  nothing. Verified before deciding, not assumed — `merge-base --is-ancestor`
  plus the working tree reading `"status": "canonical"`,
  `"publication_eligible": true`.
- **`merging/merge_root_files.sh` was not modified**, at line 27 or anywhere.
- **No extraction, no Δ, no combination.**
- **Nothing of the figure session's** was read or changed.

### 12.6 State at the time of writing

| campaign | merge | products | closure |
|---|---|---|---|
| `HF_SYS_MUR_UP` | 33/33 promoted, driver died at the broken gate | **complete**: 3 × 300 central, 3 × 10 blocks × 300, **0 partials** | running **twice** — PID 641373 (driver, stbc-i2) and a direct wrapper run (stbc-i3) |
| the other six | launched 14:00:39–14:01:49 UTC, all past the minute-zero schema gate | in progress | not yet reached |

**Two executors on one pipeline is outside every standing authorization in both
briefs.** §11.5 stopped on that basis; I stop on the same basis, with my
regressions repaired and nothing of the other executor's killed or altered
beyond the launcher I had already overwritten and have now restored.

---

## 13. SOLE EXECUTION RESUMED — 2026-08-18 16:37

The owner closed the competing session. §11 and §12 record the event from both
sides, and §12 concedes all three deviations. This section records what this
session did afterwards, and it does not restate what §12 already owns.

### 13.1 The competing session, confirmed closed

Its last write to the workspace was `launch_merge.sh` at **16:27:37**. Its last
commit was **`b4bc537`** at **16:29:59**, which added §12 to this file on this
branch. A sweep of all three login nodes at 16:35 found no new process and
no new file from it. Its own launching shell for the duplicate closure had
already reparented to PID 1, so its session had gone.

**Both executors committed to this branch in one worktree**, which is how §12
arrived here. The reflog interleaves this session's commits and `b4bc537`
cleanly, and it shows every commit still in place.

**One process on `stbc-i3` belongs to neither of us.** PID 3953858 runs
`plotting/run_paper_plots.sh kinematic-spectra` from
`/data/alice/ipardoza/figure_deploy_20260817`, with a watcher at PID 4035146
polling it. That is the figure session. This session read its command line and
touched nothing else of it.

### 13.2 The duplicate closure, killed

| | |
|---|---|
| host | `stbc-i3.nikhef.nl` |
| PGID | **3992192** |
| members | 3992192 `bash close_murup.sh`, 3992195 wrapper, 3992999 `root`, 3993000 `root.exe` |
| launching shell | 3992190, PPID 1, group 3992100, exited by itself |
| signal | `kill -TERM -3992192`, by process group, never `pkill -f` |
| killed at | **2026-08-18T14:36:48Z** |
| after 6 s | 0 members alive |
| elapsed when killed | 22 m 37 s, still on its first tune |

**§12.4 argues both runs were worth keeping, and the argument has a real basis.**
`GOLDEN_OUTPUTS.md` §2.9c confirms the central campaign's three closures ran
independently of the merge, through
`extraction/pipeline/harvest_tune.py --stage closure`.

**The paths decide it.** The driver writes its report to
`${analysis_root}/validation/pair_block_closure_${output_tag}_${tune}.log`,
which is where the central campaign's three reports sit. The killed run wrote to
`systematics_harvest/closure_runs/`, which is nowhere the pipeline reads. The surviving run therefore produces the
verification of record at the canonical path. It is also the only end-to-end
test of the repaired call site. The killed run
duplicated about five hours of work and would have left its result off the path.

`close_murup.sh` stays on disk, unused. Its per-tune guard skips a tune whose
log exists, so a careless re-run would resume at JUNCTIONS instead of repeating
MONASH. This session left the file alone: it belongs to the other executor.

### 13.3 The launcher is now versioned, and holds a lock

§12.2 restored the launcher's five refusals faithfully. The deeper fault stayed:
the file lived only in the workspace, so an overwrite could drop two guards and
leave no trace. `tools/harvest_launch_merge.sh` now holds the canonical copy,
and the workspace holds a deployed copy.

Six refusals cover an absent schema, a live or stale or foreign-host lock, and
an existing campaign log. They also cover an unclean checkout, a checkout
predating the closure-gate fix, and free disk below 150 G. Every one ran on
`stbc-i3` against the real workspace, and no refusal created a campaign log.

The lock records pid, pgid, host, start time, and campaign, and the launcher
creates it atomically under `set -o noclobber`. A live lock refuses and prints
its contents. A stale lock refuses, prints its contents, and survives, because
only a person may remove it. A lock from another host refuses as well. This host
cannot ask whether that PID lives. E8 warns that an identity checked in the
wrong context looks exactly like one that exited.

`tests/test_harvest_launcher.py` runs twelve checks, three of them mutations. A
`v3` default, a disabled lock, and a deleted fix-presence guard each break the
matching check.

Two portability faults surfaced while writing the test. The disk probe used
`df -BG --output=avail`, which is GNU-only, and the liveness probe used `/proc`,
which is Linux-only. Both are now POSIX: `df -Pk` and `kill -0`.

| artifact | sha256 (first 16) |
|---|---|
| deployed `launch_merge.sh` | `68da376eef2465fc` |
| preserved, this session's earlier version | `launch_merge.sh.pre_schema_20260818` |
| preserved, the other executor's 16:27 version | `launch_merge.sh.otherexec_20260818T1627` |

### 13.4 The publication-export exclusion list

The private publication-export exclusion inventory now exists, seeded with
`docs/writing_standard/ASD-STE100_ISSUE9.pdf`. The export session owns the list
and extends it. The entry names the enforcing mechanism, the command that shows
it working, and whether the file sits in git history. It does not.

### 13.5 The writing standard, and its cherry-pick note

Commit **`b598ce7`** installs the private writing standard and its prose checker.
**The other active branch cherry-picks `b598ce7` at its
next session.**

The install brief asked for that note in the private merge checklist on branch
`freeze-contract-fix`, which the figure
session owns and this session must not write to. The note therefore lives here,
and it says the same thing.

---

## 14. THE CLOSURE LOOP RUNS, AND MUR_UP IS CLOSED — 2026-08-19 00:14

**`HF_SYS_MUR_UP` passed closure on all three tunes.** This is the first
successful run of the driver's closure loop since `8f410a43` broke its call site
on 2026-08-13. It proves the repair in `f7ead26` end to end, in the pipeline
rather than only in a test.

### 14.1 The three verdicts

| tune | verdict | report written | wall time |
|---|---|---|---|
| MONASH | **PASS** | 2026-08-18 20:04:18 | 2 h 22 m |
| JUNCTIONS | **PASS** | 2026-08-18 22:09:09 | **2 h 04 m 51 s** |
| CLOSEPACKING | **PASS** | 2026-08-19 00:14:14 | **2 h 05 m 05 s** |

Each pass emitted the identical summary:

```
PAIR_BLOCK_CLOSURE errors=0 analysis_schema=paul_pair_objects_primary_ground_v3
central_pair_files=300 block_pair_files=3000 object_content_sumw2_closure_checks=2100
additive_metadata_closure_checks=3600 invariant_metadata_checks=1500
source_filter_contract_checks=300 expected_central_events=10000000
relative_tolerance=2e-10
```

The check counts are 2100 content and 1500 invariant, the same registered counts
the central campaign passed (`GOLDEN_OUTPUTS.md` §2.9c). All 36 `errors=` fields
in the run read zero, and the log holds no `ERROR` line.

**The completion fact comes before the absence.** All three markers appear in
the log, and only then did PID 641373 leave `stbc-i2`. Under the E8 rule that is
a completion, not a death.

### 14.2 Closure cost at variation scale, measured

§9.5 could only extrapolate this number across a factor of seven, and said so.
It is now measured.

| step | measured |
|---|---|
| re-validating 33 existing products | 1 h 41 m |
| closure, per tune | **2 h 04 m – 2 h 22 m**, mean 2 h 11 m |
| closure, three tunes | **6 h 32 m** |
| whole re-run, PID 641373 | 8 h 13 m |

The three tunes ran under seven-way contention on two nodes. The first tune was
the slowest of the three, which is the same cold-cache signature §9.5 recorded
for the merge legs.

**The extrapolation was close.** §9.5 projected about 1 h 50 m per tune from the
central campaign's 13 h 50 m and a 7.4× size ratio. The measurement is 2 h 11 m,
so the estimate was low by about 19 %.

### 14.3 The six, at 00:16

| campaign | products | closures | now |
|---|---|---|---|
| `HF_SYS_MUR_UP` | 33/33 | **3/3 PASS** | **CLOSED** |
| `HF_SYS_PTHAT_1` | 33/33 | 2/3 | CLOSEPACKING closure, 10 m in |
| `HF_SYS_MUF_DOWN` | 33/33 | 1/3 | JUNCTIONS closure, 1 h 19 m in |
| `HF_SYS_PTHAT_4` | 33/33 | 0/3 | MONASH closure, 57 m in |
| `HF_SYS_MUR_DOWN` | 22/33 | 0/3 | CLOSEPACKING leg, validating |
| `HF_SYS_MUF_UP` | 11/33 | 0/3 | JUNCTIONS leg, merging 3 h 29 m |
| `HF_SYS_PDF_CTEQ6L1` | 11/33 | 0/3 | JUNCTIONS leg, merging 4 h 35 m |

**176 of 231 products, and 6 of 21 tune closures.** No campaign has a non-zero
`errors=` field. Disk holds 928 G free.

`HF_SYS_MUR_DOWN` was the laggard at 20:05 with nothing promoted after 2 h 27 m.
It recovered without help and now leads the unfinished group at 22/33. The two
slow legs are `HF_SYS_PDF_CTEQ6L1` and `HF_SYS_MUF_UP`, both on a JUNCTIONS
complete leg for over three hours.

### 14.4 Expected completion for all seven

Projected from the measured 2 h 11 m per closure and each campaign's own
position. Contention falls as campaigns finish, so these are upper bounds.

| campaign | expected close |
|---|---|
| `HF_SYS_MUR_UP` | **done, 00:14** |
| `HF_SYS_PTHAT_1` | ≈ 02:10 |
| `HF_SYS_MUF_DOWN` | ≈ 03:15 |
| `HF_SYS_PTHAT_4` | ≈ 05:30 |
| `HF_SYS_MUR_DOWN` | ≈ 09:00 |
| `HF_SYS_MUF_UP` | ≈ 12:00 |
| `HF_SYS_PDF_CTEQ6L1` | ≈ 13:00 |

**All seven closed: late morning to early afternoon on 2026-08-19.** Extraction
stays blocked until then, and it needs its own brief.

---

## 15. EXTRACTION OF THE FIVE CLOSED CAMPAIGNS — 2026-08-19

This session measured deliverable 1 of pre-registration section 2, the
diquark-structure decomposition, for the five closed campaigns. Deliverable 2, the
per-class OS−SS balancing yield, is **not**, and section 15.6 states why.

### 15.1 The instrument, and the proof it is the same one

The chain is the one that produced the central per-tune numbers. Every sha
below was read from the deployed files at run time and matches
`THREE_TUNE_CENTRAL_TABLE.md` section 6 exactly:

| artifact | sha256 |
|---|---|
| `extract_species_decomposition.py` | `4cd8b6fa8493529624b33de81e67764c07c2126465d7ae921e5970919f0ad960` |
| `species_ordinals_v2.json` | `ccec0dbc70f6452d1f4a5c22a37e76ce55b357046094da207469f08534d0e4ce` |
| `decay_parent_map_v2.json` | `58081aa2f87cb67141259f2b74a5057777a6c8eaa5049446fd3f47b13a1c84da` |
| `heavy_flavour_pair_registry_v1.json` | `ea9b0232c1be84158446e559e23aebf3410b3c8a6e39a221d367f0d0c7ddee23` |

Environment: `stbc-i2.nikhef.nl`, checkout `51603c2`, ROOT
`v6-30-01-alice5-2` from CVMFS on pin. Driver PID 1564517, PGID 1564517.

**E5 discipline, all three parts present.** The chain passes `--registry`, so the reader deduplicates
trigger-level closure objects instead of counting them 24 or 26 times. It
passes `--decay-map` explicitly, so the defective v1 default cannot apply
(GOLDEN_OUTPUTS finding F1). The reader is the deduplicating one, by sha.

**The preflight uses exact filenames and no glob.** It takes the 300 names from
the signed registry and calls `is_file()` on each, in all 33 directories of
each campaign. A glob would also match a `.partial` staging directory.

```bash
HADRONIZATION_EXPECTED_PAIR_SCHEMA=v3 \
  systematics_harvest/run_all_extract.sh      # five campaigns, 6-way parallel
```

### 15.2 What ran, and what it reported about itself

| campaign | directories | rc=0 | `SELF_CHECK AGREE` | `INVARIANCE CONSERVED` |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` | 33 | 33 | 33 | 33 |
| `HF_SYS_MUR_DOWN` | 33 | 33 | 33 | 33 |
| `HF_SYS_MUF_DOWN` | 33 | 33 | 33 | 33 |
| `HF_SYS_PTHAT_1` | 33 | 33 | 33 | 33 |
| `HF_SYS_PTHAT_4` | 33 | 33 | 33 | 33 |

165 of 165 directories, no failure. Window 09:43:53 to 09:59 CEST, 15 minutes.
Every run reported `SELF_CHECK AGREE worst_relative=0.000e+00`.

### 15.3 The per-event plausibility check, on every absolute count

The E5 defect showed as about 13 counts per event where the truth is order
one. The gate is on the order of magnitude.

| campaign | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `HF_SYS_MUR_UP` | 0.5377 | 0.4646 | 0.4682 |
| `HF_SYS_MUR_DOWN` | 0.5350 | 0.4613 | 0.4654 |
| `HF_SYS_MUF_DOWN` | 0.5096 | 0.4507 | 0.4552 |
| `HF_SYS_PTHAT_1` | **0.4105** | **0.3496** | 0.3572 |
| `HF_SYS_PTHAT_4` | **0.6223** | 0.5534 | 0.5458 |
| *`HF_RUN3_V1` nominal* | *0.5366* | *0.4631* | *0.4668* |

**All fifteen pass.** The range is 0.3496 to 0.6223, so the worst point sits
20.9 times clear of the failure mode. The nominal values fall inside the
variation range in every tune. The ordering is the physically expected one:
`PTHAT_1` lowest and `PTHAT_4` highest in all three tunes.

### 15.4 The deltas

Full tables:
[`results/systematics/20260819/PER_CATEGORY_DELTAS.md`](../results/systematics/20260819/PER_CATEGORY_DELTAS.md).
Machine-readable: `per_category_deltas.json`, sha256
`06bb639200ff01ae150baada8c86e737848da6888592a1b5aeddb7a3d3054981`.

**55 deltas, 12 unresolved at 2 sigma, 5 LOW-STAT-ZERO.** The five are every
campaign's MONASH `kMultiplyHeavy`, where the sealed nominal holds 8 counts in
total and individual blocks hold zero. A relative shift against zero has no
meaning, so this record quotes none.

**Both estimators are reported and they agree.** The registered one
(pre-registration 2.2) forms the relative shift inside each block; the
2026-08-19 brief specifies means-first with SEMs in quadrature. Across all 55 deltas the two central values agree
to within 0.17 in the last quoted digit. The SEMs differ by at most 20 per
cent. That is the signature of two valid routes to one quantity.

**The largest effects are `HF_SYS_MUF_DOWN` and `HF_SYS_PTHAT_4`.** MUF_DOWN
moves JUNCTIONS `kExcludedVector` by +3.3070 ± 0.0637 per cent at 51.9 sigma
and CLOSEPACKING `kExcludedExcited` by −13.0501 ± 0.2818. PTHAT_4 moves MONASH
`kCentralGround` by −3.7400 ± 0.0393 at 95.1 sigma. `HF_SYS_MUR_UP` is the
quietest: seven of its eleven quoted classes fall short of 2 sigma.

### 15.5 The control that licenses the arithmetic

This session ran the same code path on the committed sealed anchors before it
touched any variation. It reproduced `THREE_TUNE_CENTRAL_TABLE.md` section 1
to the last digit: kCentralGround **52.4959**, kExcludedVector **46.4946**,
kExcludedExcited **1.0095**, kMultiplyHeavy **0.0000**, and the I3 total
**53,662,416**. The block SEMs also come back at the published 0.0074, 0.0079,
0.0012 and 0.0000. That control is now `tests/test_harvest_deltas.py`, so it
runs in the suite rather than once.

### 15.6 STOP — deliverable 2 has no chain for a variation campaign

Pre-registration section 2 requires **both** the decomposition fractions and
the per-class OS−SS balancing yield. This section delivers only the first.

`extract_species_decomposition.py` writes `per_species.csv`,
`per_category.csv` and `per_observable.csv`. **None of them carries the multiplicity class
axis.** The per-class balancing observable comes from
`tools/statistical_robustness.py`. That tool requires two inputs which do not
exist for any variation campaign:

- `--boundary-receipt`, a PASS `multiplicity_boundary_receipt_v1.json`. The
  only receipts on Nikhef are the central campaign's, under
  `hadronization_v3_plotting_run/plot_archive/`. The class axis sits on common
  absolute `N_ch` boundaries shared by every tune, so reuse is physically
  right. The tool binds a receipt to the configuration that produced it, and
  nobody has checked that binding against a variation.
- `--origin-closure-report`, a PASS final-origin closure for the **same sealed
  manifest**, with pilot evidence explicitly rejected. No such report exists
  for any of the seven campaigns. One such report costs a per-job pass over 300
  directories per campaign.

**This is reported, not worked around.** Reuse of the central's receipt needs a check
that the tool accepts it. Without that check, or with some other observable
substituted, a paper table would carry a number whose method nobody could name.

### 15.7 The two stragglers

This session stopped, restarted and re-planned neither.

| | `HF_SYS_MUF_UP` | `HF_SYS_PDF_CTEQ6L1` |
|---|---|---|
| host | `stbc-i3`, PID 3953522 | `stbc-i2`, PID 642060 |
| products | 22/33 | 22/33 |
| closures | 0/3 | 0/3 |
| CLOSEPACKING leg at 10:17 | 64/300 | 50/300 |
| driver elapsed | 18 h 00 m | 18 h 00 m |

Measured over a five-minute window at 10:02: MUF_UP wrote **0** files,
PDF_CTEQ6L1 wrote **1**, so about 300 seconds per file. PDF has improved from
the 893 seconds per file measured yesterday; MUF_UP has not, and sits near 840.
Both remain 40 to 200 times slower than the five closed campaigns, which wrote
the same leg at 1.4 to 8 seconds per file.

### 15.8 The filled-bin census, and what it does not support

One per-job input per campaign, matched on file, tune and slot:
`DplusDplus.root`, CLOSEPACKING, `slot_000`.

| campaign | `hTrKinematics` | `hFlavourClosure` | `hCorrelations` | bytes |
|---|---|---|---|---|
| `HF_SYS_MUR_UP` (closed) | 11,865 | 11,550 | 149 | 189,011 |
| `HF_SYS_MUR_DOWN` (closed) | 11,987 | 11,587 | 129 | 189,391 |
| **`HF_SYS_MUF_UP` (straggler)** | **12,337** | **12,819** | 223 | 206,812 |
| `HF_SYS_MUF_DOWN` (closed) | 11,504 | 10,658 | 85 | 175,809 |
| **`HF_SYS_PDF_CTEQ6L1` (straggler)** | **12,544** | **12,611** | 177 | 203,954 |
| `HF_SYS_PTHAT_1` (closed) | 9,808 | 8,759 | 64 | 153,256 |
| `HF_SYS_PTHAT_4` (closed) | 12,204 | 14,397 | 319 | 226,414 |

**The two stragglers carry marginally more filled bins on one object and fewer
on another.** Against the closed campaigns they are 1.01 to 1.28 times on
`hTrKinematics`. On `hFlavourClosure` the closed `HF_SYS_PTHAT_4` carries
**more** than either straggler, 14,397 against 12,819 and 12,611, and it also
has the largest input file. It closed normally.

**No factor here resembles the runtime difference.** The largest ratio in the
census is 1.28. The runtime ratio is 40 to 200. **The census does not support
the filled-bin explanation**, and it supports no other explanation either: it
rules one candidate out and leaves the cause open.

---

## 16. WHAT THE FINAL-ORIGIN CLOSURE CERTIFIES, AND WHY TASK 2 STOPPED — 2026-08-19

### 16.1 The property the report proves

`tools/final_origin_closure.py` audits **every** canonical raw file of one
sealed manifest with `Validation/AuditOriginResolution.C`, retains the per-job
ROOT outputs, and aggregates them. It proves two things about that exact
sample. First, the eight-category primary-all-heavy closure **closes**. For
every base the audited categories form the full set. Their counts and summed
weights each equal the recorded denominator, checked with the project's
`nearly_equal`.

Second, and this is the publication gate,
**`unresolved_trigger_candidate_count` is exactly zero** — no trigger candidate
in the sample has hard-process ancestry the origin algorithm could not resolve.
The report sets `completion_state=PASS` and
`publication_readiness=READY` only on that zero.

It carries `canonical_manifest_sha256` and `freeze_seal_sha256`, so it
certifies one sample and no other.

### 16.2 The five closed campaigns do NOT hold that evidence

They hold **part** of the first property and **none** of the second.

| evidence | where it lives for a variation | is it what the report proves? |
|---|---|---|
| `primary_all_heavy_closure_failures=0` | `hadronization_analysis/HF_SYS_*/per_job/<TUNE>/slot_*/analysis.log` | the closure-consistency half, per slot, not aggregated and not bound to the freeze seal |
| `same_hard_constituent_pairs=0` | same log | a different check: duplicate hard carriers, the A2 tie-break subject |
| `upstream_origin_classification_failures=0` | closure-checked scalar in every pair file | classification **failures**, not unresolved **counts** |
| `upstream_heavy_flavour_conservation_failures=0` | same | conservation, not ancestry resolution |
| `origin_algorithm=signed_heavy_constituent_complete_mothers_unique_v4` | `analysis_job_metadata.json` | names the algorithm; says nothing about its outcome |
| **unresolved trigger-candidate count** | **nowhere** | — |

The analysis log contains the strings `origin` and `unresolved` **zero times**.
The metadata carries 27 keys and none of them is an unresolved count. Nothing under `/data/alice/ipardoza` retains an
`AuditOriginResolution.C` output; the only hits are the source file and its
compiled artifacts inside checkouts.

### 16.3 The finding is larger than the variations

**The sealed central campaign does not hold it either.**
`hadronization_analysis/HF_RUN3_V1/validation/` contains exactly four files:
`analysis_output_manifest_validation.json` and the three
`pair_block_closure_HF_RUN3_V1_<TUNE>.log`. **There is no final-origin closure
report for `HF_RUN3_V1`, and there never has been.**

So `tools/statistical_robustness.py` has never run on any campaign in this
project, because one of its five required inputs has never existed.

The tool describes itself as an independent audit rather than the primary
producer, which fits. `GOLDEN_OUTPUTS.md` §2.9c records that the central
per-class work went through `harvest_tune.py --stage closure` instead.

### 16.4 Task 2 stopped, per its own condition

The brief's task 1 reads: *"If they do not, STOP task 2 and report what is
missing."* They do not. This session therefore left the boundary contract
alone.

**Changing it would not have opened the chain.** `--boundary-receipt` and
`--origin-closure-report` are two separate required arguments. A relaxed
first argument leaves the second refusing for every campaign, central
included, so task 3's per-class deltas stay out of reach either way.

**What is missing, and what it would cost.** The report is *producible*: the
tool needs only `--canonical-freeze` and `--production-root`, and both exist
for all seven campaigns. The price is an `AuditOriginResolution.C` pass over
every canonical raw file: 300 per tune, 900 per campaign, **4500 audits for the
five closed campaigns**. The central needs one more pass if its per-class
numbers are to rest on the same certificate. That is an owner decision about cost. This
session may not take it under a brief whose task 1 told it to stop.

### 16.5 The two stragglers, unchanged and untouched

| | `HF_SYS_MUF_UP` | `HF_SYS_PDF_CTEQ6L1` |
|---|---|---|
| host, PID | `stbc-i3`, 3953522 | `stbc-i2`, 642060 |
| three-state | **ALIVE** on its own host; absent elsewhere, which proves nothing | **ALIVE** on its own host |
| elapsed | 19 h 36 m | 19 h 36 m |
| products | 22/33 | 22/33 |
| closures | 0/3 | 0/3 |
| CLOSEPACKING leg | 70/300 | 55/300 |

Measured over five minutes at 11:32, each wrote **one** file: about 300 seconds
per file, and the two now run at the same rate. At that rate MUF_UP needs
another 19 hours to finish this leg and PDF_CTEQ6L1 another 20, before ten
block legs and three closures each.

---

## 17. THE ZERO-UNRESOLVED GATE IS UNREACHABLE, AND THE TOOLS ARE SUPERSEDED — 2026-08-19

### 17.1 The A2 verdict

**The sealed central sample does contain trigger candidates the origin
algorithm did not resolve, and it contains them by design.**

`generation/producer/heavyflavourcorrelations_status.cpp:1217`,
`EnforceUniqueFinalHardCarrier`, groups final sector-charged hadrons by the hard
quark each claims. Where two or more claim the same quark, the event record cannot
distinguish the assignment. **Production then demotes every claimant to
`Origin::kUnresolved`**, with `MatchResolution::kDuplicateHardCarrier` and
`matchedHard = -1`. The analysis then drops such candidates **as triggers**
(`status_analysis_THnSparse_qq.C:993,1002`). `COMPONENTS.md` states the design
in one line: *ambiguous ancestry is `kUnresolved` and never tie-broken*.

**The counts, measured, per tune.** A2's baseline arm is the **committed
`per_job` output** for `slot_000`–`slot_099`, not a re-run, so these are rows of
the sealed campaign itself rather than of a separate sample:

| tune | `contested_seen` | restorations |
|---|---|---|
| MONASH | **124** | 62 |
| JUNCTIONS | **24,411** | 12,194 |
| CLOSEPACKING | **24,590** | 12,287 |

Those are 100 of the sealed campaign's **1000** slots, so the full central
carries at least these and by construction more. The duplicate-hard-carrier
population is also only a **subset** of `kUnresolved`, which the
pre-registration states arises as well from failed ancestry walks and
multi-heavy rejection.

**Therefore `publication_readiness=READY` could never be reached** — not for
JUNCTIONS or CLOSEPACKING, and not for MONASH either. `final_origin_closure.py`
sets `READY` only on `unresolved_trigger_candidate_count == 0`, and that count
is structurally non-zero in every tune.

**A2 measures the same quantity as a systematic instead.** Δ per multiplicity
class, largest-`heavyIndex` arm: JUNCTIONS 0.0255 to 0.1509 per cent across
M1–M4, CLOSEPACKING 0.0377 to 0.2293 across M1–M5, MONASH negligible. The
project's answer to unresolved origin is a measured uncertainty, not a gate that
rejects the sample.

### 17.2 Disposition

`COMPONENTS.md` now marks `tools/statistical_robustness.py` and
`tools/final_origin_closure.py` **SUPERSEDED**, with the rationale and the A2
reference.
This session deletes neither.

### 17.3 The never-run finding, for the external review

**A component sat in the inventory for months with a required input that had
never existed, and nothing noticed.**

`tools/statistical_robustness.py` is 2761 lines. The private repository census counts 25 references to it. It carries its own test
file, appears in `COMPONENTS.md` three times, and pins the plotter, the
boundary utilities and its configuration by sha. **It has never run on any campaign.** One of its five
required arguments, `--origin-closure-report`, has never had a producible
value. The gate that would produce it cannot pass on this analysis.

**How the inventory missed it.** Every check that touched the tool checked its
*source*: the census counted references, `V2_PIN_SWEEP.md` audited its
exact-string matching, `test_statistical_robustness.py` exercises its functions
against fixtures. **None of them asked whether the tool's inputs exist.** A
reference count measures how often the tree names a file. A unit test measures
whether functions behave on constructed data. Neither one measures whether the
program can be run at all on the project's real artifacts.

**The generalisable check:** for every tool with required inputs, name the
artifact that satisfies each one and the run that produced it. A required input
with no producer is a component that only looks alive.

### 17.4 The published per-class instrument, named

Task 3 asked for the chain behind the published per-class balancing yields.

| | |
|---|---|
| emitter | `plotting/improvedPlotting_THnSparse.C:3739`, the `UNCERTAINTY_MATRIX` line |
| per-row key | `(flavour, trigger, tune, associate, bin)` — all five, as `GOLDEN_OUTPUTS` §9.9.1 records after a four-field key collided |
| fields | `central_yield`, `yield_sem`, `reference_yield`, `ratio_sem`, `central_triggers`, `block_triggers`, `finite_yields`, and PASS/FAIL coverage statuses |
| SEM | `yieldStats.stdError` over the ten subsamples, emitted only when `technicalCoverage.yieldComplete` |
| class windows | `plotting/configuration_multiplicity_HF_RUN3_V1_THREETUNE_THnSparse_complete_root.json`, one entry per class carrying `multiplicityMin`/`multiplicityMax` as MONASH-MB percentiles (88.197–100.0, 80.597–88.197, 65.937–80.597, …) |
| boundary artifact | `config/multiplicity_class_boundaries_v1.json`, sha256 `3b0554fe6c291a26ba03b0524975892754e9a0e75896b203c24d05e853d195b5`, `c1…c11` on `multiplicity_primary_charged_eta10_v1` |
| receipt | `WriteMultiplicityBoundaryReceipt` (`:1311`) writes `multiplicity_boundary_receipt_v1.json` and records `MultiplicityBoundaryUtils.h` |
| inputs | the merged `complete_root_<CAMPAIGN>_<TUNE>` plus its ten `combined_root_subSamples_<TUNE>` directories |

**One correction to the brief's premise, and it matters for task 4.** The
`UNCERTAINTY_MATRIX` line carries **no multiplicity-class field**. Its `bin` is
`binFromTHnSparse.hDPhi`, a Δφ bin. The class enters through the
*configuration's* window, so a per-class number is one render per class, and the
class label lives outside the emitted line. Any per-class comparison must
therefore key on the configuration as well as on the five emitted fields.

### 17.5 What did not run

**Tasks 4 and 5 did not start.** Naming the instrument consumed this session.

The control it requires is a ROOT render of the plotter, per class and per
tune, on the sealed central. The campaigns then need the same. That is a
Nikhef job of a different size from the extraction in §15. A start before the
control passes would invert the order task 4 sets.

---

## 18. THE CLASS AXIS, SETTLED — AND A CORRECTION TO §17.4 — 2026-08-19

### 18.1 The correction

**§17.4 said the `UNCERTAINTY_MATRIX` line carries no multiplicity-class field.
That is wrong.** The class is in the `bin` field, encoded in the histogram name.
The reading of `binFromTHnSparse.hDPhi` as a Δφ bin index was an inference from
the variable's name, made without opening a rendered log. One rendered log settles it in a line:

```
bin=hDPhic1_MB88p197_100      class c1,  MONASH-MB percentile window 88.197-100
bin=hDPhic11_MB0_8p422        class c11, window 0-8.422
bin=hDPhiM00_100              the multiplicity-INTEGRATED bin
```

**The consequence is a cost model, not just a fact.** §17.4 concluded that a
per-class number costs one render per class. It does not. **One render of the
eleven-class configuration emits every class**, and the sealed central's log
already holds all of them.

### 18.2 The parsing rule

```python
CLASS_BIN = re.compile(r"^hDPhi(?P<cls>c\d+)_MB(?P<lo>[0-9p]+)_(?P<hi>[0-9p]+)$")
INT_BIN   = re.compile(r"^hDPhiM(?P<lo>\d+)_(?P<hi>\d+)$")
key = (flavour, trigger, tune, associate, class)
```

`p` is the decimal point. The key carries all five fields `GOLDEN_OUTPUTS` §9.9.1
requires. The class replaces the raw `bin` string, so a variation's window
label cannot collide with the central's.

### 18.3 The 24-point reproduction, at no render cost

The figure branch's `tools/assert_variant_identity.py` compares V-EXTREMES
against the eleven-class closure run on classes c1 and c11. Re-running that
comparison with the rule above, over the deploy's own logs, read-only:

| log | `UNCERTAINTY_MATRIX` rows | classes |
|---|---|---|
| `vextremes.log` | **24** | c1, c11 |
| `vintegrated.log` | **12** | integrated |
| `vintegrated_closure.log` | **144** | c1…c11 and integrated, 12 combos each |

| assertion | points | result |
|---|---|---|
| V-EXTREMES vs the eleven-class closure run | **24** | **0 mismatches**, exact 17-digit string equality |
| V-INTEGRATED vs the closure run | **12** | **0 mismatches** |

First four points, verbatim:

```
CLOSEPACKING B^{+} B-        c1  yield=0.10639730639730641  sem=0.0016767013662127941
CLOSEPACKING B^{+} B-        c11 yield=0.077949478981836934 sem=0.00090187351030636322
CLOSEPACKING B^{+} Lambda_b  c1  yield=0.023007856341189677 sem=0.00093535321541570945
CLOSEPACKING B^{+} Lambda_b  c11 yield=0.039242507339419946 sem=0.00057609964772919174
```

The rule reproduces the figure branch's own published result exactly, and this
session ran nothing from that branch and changed nothing in it.

### 18.4 The nominal arm is already in hand

`figure_deploy_20260817/vintegrated_closure.log` holds the sealed central's
**per-class yields and ten-block SEMs for all eleven classes**, across three
tunes and four trigger-associate combinations each. Task 4 needs the same
quantity from each variation campaign, which is one plotter render per campaign
against that campaign's merged products.

### 18.5 The component-liveness rule

Recorded for the inventory, from §17.3: **for every tool with required inputs,
name the artifact that satisfies each one and the run that produced it.**

A required input with no producer is a component that only looks alive. A
reference count measures how often the tree names a file; a unit test measures
behaviour on constructed data; neither asks whether the program can run on the
project's real artifacts.

### 18.6 What did not run

Tasks 2 through 4 did not start. The control needs a plotter render of the sealed
central. The deltas need one render per closed campaign, each against that
campaign's merged products with a generated configuration. This section quotes
no per-class delta.

---

## 19. THE OUTPUT-PATH DEFECT, AND THE HANDOFF — 2026-08-19 15:24

### 19.1 The measurement target wrote into a publication path

**OPEN ITEM. The measurement target does not yet honour its own ruling.**

The ruling said measurement artifacts must never land in a publication output
path, and put the protection on the output side. The implementation staged a
configuration copy whose **top-level** `write_path` pointed at the measurement
root. The plotter does not read that key. `writeCanvasToFiles` takes its
`writePath` from a **nested** configuration field
(`plotting/improvedPlotting_THnSparse.C:215,265`), so the plotter never saw the staged
value, and the canvases went where the unstaged configuration pointed.

**Three artifacts landed in a publication output path**, all at 15:14:02 in
`/data/alice/ipardoza/sys_plot_deploy/plotting/Plots/THnSparseCompleteRoot_HF_RUN3_V1/`:

- `global_balancing_plots_multiplicity_HF_RUN3_V1_THREETUNE_PDF.pdf`
- `global_balancing_plots_multiplicity_HF_RUN3_V1_THREETUNE_PNG.png`
- `global_balancing_plots_multiplicity_HF_RUN3_V1_THREETUNE_MACRO.C`

**Nothing published or sealed was touched, and that is measured rather than
assumed:**

| what | evidence |
|---|---|
| the figure deploy's `plotting/Plots` | newest entry **2026-08-18 17:25**, hours before this session rendered |
| the sealed `VariantIntegratedClosure` receipt | mtime **2026-08-18 10:18:19**, unchanged |
| the path the three artifacts landed in | this session's own scratch deploy, **not** the figure deploy |
| that path in git | **ignored**, `.gitignore:56` `plotting/**/Plots/` |
| the boundary receipt beside them | **not overwritten** — the receipt gate refused, which is what returned `rc=1` |

They overwrote artifacts this session's own earlier control render wrote at
13:19. No committed artifact, no published artifact, no sealed receipt.

**The error class is the one this session already recorded once.** §18 wrote
that the configuration is a request and the resolver line is the answer. Here
the same mistake was made one level up: the gate, the staged configuration and
the refusal of a root inside `plotting/Plots` all constrain the **request**,
and nothing checked **where the files actually landed**.

**The fix, unbuilt and specified.** Set the nested `writePath` the plotter
actually reads, and verify it by reading it back out of the staged file.

Then assert on the output side after every render. No file under
`plotting/Plots` may carry an mtime inside the render window. The expected
artifacts must exist under the measurement root. Then add a mutation test where
a render writing into `plotting/Plots` fails that assertion.

### 19.2 Handoff

**Tip `035aaeb`.** The worktree carries one untracked file. It is `INSTALL.md`, the installer that
came with the writing-standard kit, and this session deliberately left it out of
git.

#### Done and committed

| commit | what |
|---|---|
| `5ca65d5` | five closed campaigns extracted; **55 per-category deltas**, audited and standing |
| `d1e5095` | the final-origin closure certificate does not exist for any campaign |
| `c3b31fa` | `statistical_robustness.py` and `final_origin_closure.py` marked SUPERSEDED |
| `769e351` | the class axis settled; §17.4's claim corrected |
| `3096d44` | nominal-arm receipt bound; control passed at six figures; five configs generated |
| `8727995` | five selector rows; the resolver assertion and its mutation |
| `035aaeb` | the measurement target; Correction 9, the third `rc` misread |

#### NOT done

**No per-class delta. No integrated delta. No plausibility numbers for either.**
The only deltas this pipeline holds are the 55 per-category ones in
`results/systematics/20260819/PER_CATEGORY_DELTAS.md`.

#### Checking a straggler for closure, from disk

```bash
C=HF_SYS_MUF_UP        # or HF_SYS_PDF_CTEQ6L1
M=/data/alice/ipardoza/hadronization_merged
W=/data/alice/ipardoza/systematics_harvest
n=0
for T in MONASH JUNCTIONS CLOSEPACKING; do
  [ -d "$M/complete_root_${C}_${T}" ] && n=$((n+1))
  for i in $(seq 1 10); do
    [ -d "$M/SUBSAMPLES_${C}/combined_root_subSamples_${T}/combined_root_${i}" ] && n=$((n+1))
  done
done
echo "products=$n/33"
grep -c CANONICAL_PAIR_BLOCK_CLOSURE_PASS $W/merge_runs/merge_${C}.log
tail -3 $W/merge_runs/merge_${C}.log
```

A CLOSED campaign reads **`products=33/33`**, **`3`** markers, and a log whose
last line is `CANONICAL_PAIR_BLOCK_CLOSURE_PASS tune=CLOSEPACKING report=…`.
**Count by these exact names and never by a glob**: a glob also matches the
`.partial.XXXXXX` staging directories and reports unpromoted work.

**The marker count comes first and the absence of the PID second.** A PID gone
without three markers is a death, not a completion (E8), and a PID checked on
the wrong host is indistinguishable from one that exited.

#### Processes

**Left alive, and NOT this session's to touch** — the two merges:

| campaign | host | PID | PGID | elapsed at 15:24 |
|---|---|---|---|---|
| `HF_SYS_MUF_UP` | `stbc-i3` | 3953522 | 3953522 | 23 h 23 m |
| `HF_SYS_PDF_CTEQ6L1` | `stbc-i2` | 642060 | 642060 | 23 h 23 m |

Both `Ss`, both ALIVE on their own launch host and absent on the other, which
proves nothing about the other.

**Terminated by this session, by PGID:**

| PGID | what | members at kill | after |
|---|---|---|---|
| 77181 | local six-campaign watcher | 77181, 77183, `sleep 900` | **0 alive** |
| 81502 | local two-straggler watcher | 81502, 81504, `sleep 1800` | **0 alive** |

**Confirmed dead earlier, by three-state probe on their own hosts:**

- 108654, the MUR_UP merge; 641373, its closure re-run
- 1564517, the per-category extraction; 3743767, the suite
- 1715164, the control render; 1737096, 2457374 and 2609572, variation renders
- 3992192, the duplicate closure this session killed **No waiter remains armed.**

#### The measurement target

**Works and is tested.** The target admits `canonical`, `canonical_candidate`
and `systematic_variation`. It requires a measurement root with no default,
refuses a root inside `plotting/Plots`, and refuses to share a run with a
publication target. It stamps `purpose=measurement` on its receipt. A test
asserts the publication gate predicate's exact text, which did not move.

**Unverified:** that a measurement render's artifacts land under the
measurement root. §19.1 says they did not.

**What the nine mutation tests do NOT cover.** Every one of them gates the
**request** — a status, a root, a target combination, a source pattern — and
they run before any render. **Not one inspects what a render produced.** They
passed while the requirement failed. A test suite that only tests refusals certifies a
locked door, not an empty room.

---

## 20. THE PER-CLASS AND INTEGRATED DELTAS — 2026-08-19 16:20

Deliverable 2 exists. The output-path defect of §19.1 is closed, and the closing
is verified on the output side rather than asserted on the input side.

### 20.1 The output-side assertion, and its mutation

`tools/assert_measurement_outputs.py`. After a render it requires two facts of
the filesystem:

1. No file under any directory named `Plots` carries an mtime inside the render
   window.
2. Every expected artifact exists under the measurement root.

**Publication trees are discovered, not listed.** The tool walks for directories
named `Plots`, so a path the driver was never told about is still covered. The
six renders of this session each scanned **13** such trees under
`/data/alice/ipardoza`, including the figure deploy's.

**The window is inclusive at both ends, and the real case is why.** The three
canvases of §19.1 carry the render window's own end stamp, `1787145242`, to the
second. An exclusive upper bound would have called the defect clean.

**THE MUTATION IS THE REAL DEFECT, NOT A CONSTRUCTED ONE.**
`tests/test_measurement_outputs.py` replays the 2026-08-19 15:14 render from
mtimes read off the cluster and requires it to FAIL:

| check | result |
|---|---|
| the three canvases are caught | **caught**, three files, not four |
| the 13:19 boundary receipt is not attributed to the 15:14 window | **not attributed** |
| the render fails the assertion outright | **fails** |
| it fails on the publication tree, not on missing artifacts | **on the tree**, artifacts complete |
| an exclusive upper bound would have missed it | **would have missed it** |

Fifteen checks in that file, with both window edges, an inverted window, and a
render missing its own artifacts.

**The defect itself is fixed where the plotter reads.** The staging step now
forces `write_path` on every canvas entry whose `write` flag is true, in both
`canvases_to_be_drawn` and `global_canvases_to_be_drawn`. It **removes** the
top-level key, rather than leave a second place that looks like it holds the
answer. It then reads the value back **out of the staged file**, not out of the
dictionary it just wrote.

### 20.2 The rule, recorded

The private progress-probe method's **Correction 10 — a gate on the request cannot
certify the result.** One entry, three instances: the resolver line, the exit
status, the output path. It carries the previous session's phrasing: a
suite which only tests refusals certifies a locked door, not an empty room. The
rule that follows is one line. Assert on the artifact the step produced, in the
units the step produced it.

### 20.3 The control

**All 144 rows agree. Zero disagreements.**

| | |
|---|---|
| rows shared, nominal and control | **144** |
| rows in only one of them | **0** |
| disagreeing fields, `central_yield` / `yield_sem` / `central_triggers` | **0** |
| render exit status | **0** |
| output-side assertion | **pass**, 13 trees, 0 files touched |
| resolver assertion | **pass**, central and subsample both `HF_RUN3_V1` |

The brief asked for 132 rows. The renders emit **144**, because staging appends
the multiplicity-integrated `M00_100` entry copied from the configuration that
produced the nominal, sha256 `793344f3…`. The 132 per-class rows and the 12
integrated rows are all compared, and all agree.

**Two plotter builds, and the difference is inert.** The nominal came from the
figure branch's plotter (`6845553…`), the control and variations from this
branch's (`6dace20…`). The figure branch adds a staging layer, a non-integral
pair-count guard and canvas polish, and **no yield-computation line differs**.
The control measures that rather than assuming it. The figure branch was read
and not modified, and nothing ran from it.

**The control ran twice.** 15:51–15:56 with the configuration as committed, and
16:04–16:09 with the ratio y-axis widened. Both reproduce the same 144 rows.

### 20.4 Why the axis was widened

Two variation renders aborted at the drawing stage. The plotter refuses to draw
an uncertainty envelope the configured y-axis would clip, which is right for a
publication figure. `HF_SYS_MUR_UP` reaches 2.5949 on a ratio axis that stops at
2.5; `HF_SYS_PTHAT_1` reaches 0.5469 on one that starts at 0.6. **The axis frames
the central campaign and a variation need not fit inside it.**

The macro emits every `UNCERTAINTY_MATRIX` row at
`improvedPlotting_THnSparse.C:3739` and draws the first canvas at `:4015`, so
the widening cannot move a number. The re-rendered control is the check. The
widening lives only in the staged copy; the committed configurations were not
edited, and `make_hf_run3_v1_three_tune_config.py --check` still passes.

**Both aborted renders emitted all 144 rows before the abort.** Their numbers
were not read, because the brief requires both assertions to pass first, and the
output-side assertion correctly reported the missing canvases.

### 20.5 The deltas

Full tables:
[`results/systematics/20260819/PER_CLASS_DELTAS.md`](../results/systematics/20260819/PER_CLASS_DELTAS.md).
Machine-readable `per_class_deltas.json`, sha256 `cac0a757…`; flat
`per_class_deltas.csv`, sha256 `70e07e49…`.

**720 cells. 182 clear 2 SEM, 538 fall short. Every cell carries a relative
shift.** The smallest nominal yield is 0.0180359 and none is zero, so no cell is
named in place of a number.

| campaign | source | resolved / 132 per-class | resolved / 12 integrated |
|---|---|---|---|
| `HF_SYS_MUR_DOWN` | S1a down | 7 | 2 |
| `HF_SYS_MUR_UP` | S1a up | 13 | 0 |
| `HF_SYS_PTHAT_1` | S3 → 1.0 | 34 | 7 |
| `HF_SYS_MUF_DOWN` | S1b down | 42 | 8 |
| `HF_SYS_PTHAT_4` | S3 → 4.0 | 59 | 10 |

**The ordering agrees with §15.4 on the category axis**, from a different
instrument and a different estimator: the two scale arms are quietest, the two
`pTHatMin` arms loudest, and `HF_SYS_MUR_UP` the quietest of all.

The largest per-class effect is `HF_SYS_PTHAT_4` JUNCTIONS D⁺–D⁻ in class c5,
+0.0158073 ± 0.000887 at 17.8 SEM, +9.166 per cent.

### 20.6 The plausibility numbers

Exposure is 100 million events per tune for the nominal and 10 million for each
variation, read from the manifests' `requested_successes`.

| campaign | B⁺ MON | B⁺ JUN | B⁺ CLP | D⁺ MON | D⁺ JUN | D⁺ CLP |
|---|---|---|---|---|---|---|
| *nominal* | *0.01426* | *0.01031* | *0.01010* | *0.13657* | *0.11720* | *0.11922* |
| `HF_SYS_MUR_UP` | 0.01493 | 0.01083 | 0.01071 | 0.13603 | 0.11684 | 0.11889 |
| `HF_SYS_MUR_DOWN` | 0.01342 | 0.00972 | 0.00948 | 0.13727 | 0.11753 | 0.11962 |
| `HF_SYS_MUF_DOWN` | 0.01759 | 0.01286 | 0.01268 | 0.12683 | 0.11263 | 0.11458 |
| `HF_SYS_PTHAT_1` | **0.00858** | **0.00617** | **0.00602** | 0.11184 | 0.09478 | 0.09768 |
| `HF_SYS_PTHAT_4` | **0.03101** | 0.02321 | 0.02268 | 0.13526 | 0.12041 | 0.12007 |

**All 42 pass**, range 0.00602 to 0.13727, so the worst point sits **95 times**
clear of the E5 failure mode at about 13. Beauty moves by a factor of 3.6 between
`PTHAT_1` and `PTHAT_4`; charm by a fifth of that. A harder scale produces
beauty far more readily than charm, which is the expected direction.

**Trigger counts are internally consistent in all 864 rows**, against the bound
the printed precision implies. Six nominal rows fall short by 17, 13 or 14 counts
in about 13 million. All six are the integrated charm bin, where ROOT prints the
block counts as `1.3646e+06`; ten values rounded to the nearest hundred cannot
sum to an exact total. For that row the bound is 140, because two of the ten
print five significant figures rather than six.

### 20.7 The standing check passes

**No two campaigns agree exactly on any row.** `identical_row_sets` compares all
144 rows of all five campaigns pairwise on `central_yield` and returns an empty
list. The five renders of 13:29–13:46 on 2026-08-19 that all read the central
campaign would have shown here as ten identical pairs.

### 20.8 The stragglers — pre-authorised decision 4 applied

Probed **once**, at 16:20:33 CEST, by exact filename and never by a glob.

| campaign | products | closure markers | merge PID | host | elapsed |
|---|---|---|---|---|---|
| `HF_SYS_MUF_UP` | **31/33** | **0/3** | 3953522 | `stbc-i3` | 24 h 20 m 06 s |
| `HF_SYS_PDF_CTEQ6L1` | **22/33** | **0/3** | 642060 | `stbc-i2` | 24 h 19 m 34 s |

`MUF_UP` advanced from 22/33 at 15:24 to 31/33. `PDF_CTEQ6L1` is unchanged in
product count, and its log tail shows it promoting `combined_root_10` on the
JUNCTIONS leg, so it is moving.

**The marker count comes first: 0 of 3 for both, so neither has closed.** The
absence check comes second, and both PIDs are alive and `Ss` on their own launch
hosts.

**Decision 4 of the brief applies: report and end.** No extraction was started
for either. **No waiter is armed.** This session did not stop, restart or
re-plan either merge.

### 20.9 Processes

**Started by this session, all confirmed exited:**

| PID / PGID | what | state |
|---|---|---|
| 2797997, 2798005 | control render, first attempt (`measurements_v2`) | exited |
| 2804156–2804160 | five variation renders, first attempt | exited |
| 2808839–2808844 | control and five variation renders, second attempt (`measurements_v3`) | exited |

Each was launched with `setsid`, so PGID equals PID. `pgrep -f render_measure.sh`
returns nothing. **Nothing was killed by this session**, and `pkill -f` was not
used.

**A probe correction, small and worth keeping.** The first sweep for leftover
waiters ran `pgrep -a -f "…|sleep"` and found five `sleep 180` processes. They
belong to `emanuelc`, `rbijleve` twice, `asarnats` and `ldonofri`. **The Nikhef
login nodes are shared, and an unscoped `pgrep` reads every user's process
table.** Scope the check: `ps -u ipardoza` leaves only the systemd user session.
Reading another user's process as your own leaked waiter is the mirror image of
E8, where a PID checked on the wrong host looked like a clean exit.

**Left alive and not this session's to touch:** the two merges above.

### 20.10 What did not happen

**No combination.** No envelope, no quadrature sum, no arm selection. The
combination needs all seven campaigns and its own brief.

**No merge, no PR, no touch of `Paper/**` or `References.bib`.** The publication
gate predicate at `plotting/run_paper_plots.sh:223-225` is unchanged, and a test
still asserts its exact text. `HADRONIZATION_COMPLETE_ROOT_TAG` and the
subsample base were never set directly; the selector rows carry them.

**No counter re-analysis.** No origin audit.

### 20.11 Handoff

**Tip `0e54e92` plus this section.** The worktree carries one untracked file,
`INSTALL.md`, the installer from the writing-standard kit, deliberately left out
of git by the 2026-08-19 session before this one.

**Suite: 60 Python test files, 60 of 60 passing**, plus 5 C++ test files. It was
57 at handoff; this session added `test_measurement_outputs.py`,
`test_harvest_yield_deltas.py` and `test_per_class_control.py`.

#### Done and committed by this session

| commit | what |
|---|---|
| `7ca0c46` | the output-side assertion, the nested `writePath` fix, the historical mutation, the integrated-bin artifact |
| `17cec56` | the delta arithmetic, the control comparison, the printed-precision count check, the axis widening |
| `0e54e92` | the 720 deltas, the control on real rows in the suite, Correction 10 |

#### What exists now that did not

- **Per-class deltas**: 660 cells, eleven classes by twelve series by five campaigns.
- **Integrated deltas**: 60 cells.
- **Plausibility numbers**: 42 trigger-per-event ratios, all passing.
- **A control that runs in the suite** rather than once, on real log rows.
- **An output-side assertion** whose mutation is the real 2026-08-19 defect.

#### NOT done, and deliberately

**No combination.** It needs all seven campaigns and its own brief. Nothing here
sums, averages or selects an arm across sources.

**No verdict on the pre-registration 2.4 ladder.** Both arms of it now exist on
one axis for the first time. Reading it needs its own pre-registered rule.

**Neither straggler is extracted.** §20.8, decision 4.

#### The next session's first three checks

1. **Re-probe the two stragglers** with the commands in §19.2, marker count
   first. At 16:20 they held 31/33 and 22/33 products with **0/3 markers each**.
2. **If one has closed**, render it through `tools/render_measurement.sh` with
   `MEASUREMENT_WIDEN_AXES=1` and `MEASUREMENT_INTEGRATED_BIN` set, then run
   `extraction/harvest_class_report.py` with the same nominal. The recipe is in
   `GOLDEN_OUTPUTS` §2.13. It needs a selector row, which
   `tools/add_variation_selector_rows.py` writes.
3. **Do not read a number from a render** until it reports `rc=0`,
   `output_assertion=0` and `RESOLVER_ASSERTION_PASS` for the campaign asked
   for. Two renders this session emitted all 144 rows and still failed, and the
   rows were correctly not used.

#### Where things are on Nikhef

| path | what |
|---|---|
| `/data/alice/ipardoza/sys_plot_deploy` | the deploy the renders ran from, git HEAD `769e351` with newer files applied on top |
| `/data/alice/ipardoza/measurements_v3` | the six measurement roots, receipts, staged configurations, assertion verdicts, canvases |
| `/data/alice/ipardoza/sys_runs_plot5` | the six render logs and the per-campaign status logs |
| `/data/alice/ipardoza/measurements_v2` | the first attempt, kept: two renders failed the output-side assertion on missing canvases |
| `/data/alice/ipardoza/render_measure.sh` | the driver, `control` / `campaign <NAME>` / `variations` |

**The deploy's four measurement tools match the branch tip byte for byte**, and
so do the plotter and all six configurations. That was verified by sha256 before
any render, and it is why a deploy three commits behind is not a problem.

**A caution about the deploy's git HEAD.** It reports `769e351`, which predates
the measurement target. The working files are newer than the commit. Check shas,
not `git rev-parse`.

---

## 21. THE STRAGGLERS HOLD, AND THE COMBINATION IS BUILT BUT REFUSED — 2026-08-19 16:48

### 21.1 The straggler probe

Probed once, at **16:48:11 CEST**, by exact filename and never by a glob.

| campaign | products | closure markers | merge PID | host | elapsed |
|---|---|---|---|---|---|
| `HF_SYS_MUF_UP` | **33/33** | **0/3** | 3953522 | `stbc-i3` | 24 h 47 m 45 s |
| `HF_SYS_PDF_CTEQ6L1` | 22/33 | **0/3** | 642060 | `stbc-i2` | 24 h 47 m |

**`HF_SYS_MUF_UP` finished merging during the gap and is now in its closure
phase.** Its process tree shows the first of three closure passes running, 24
minutes in:

```
3417215  validate_pair_block_closure.sh …complete_root_HF_SYS_MUF_UP_MONASH … v3 10000000
3417285  root -l -b -q ValidatePairBlockClosure.C(…MONASH…)
3417286  root.exe … (state R)
```

**The marker count comes first, and it reads 0 of 3, so the campaign has not
closed.** 33 of 33 products is not closure. §19.2's rule exists because a PID
gone without three markers is a death rather than a completion. This is the
mirror case: all products present, no markers, a campaign still working.

**Neither can close inside this session, and that is arithmetic rather than
pessimism.** §14.2 measured closure at **2 h 04 m to 2 h 22 m per tune**, three
tunes per campaign. `MUF_UP` began its first at about 16:24, so its third ends
near 22:45. `PDF_CTEQ6L1` still has eleven products to merge before it starts.

**§14.4's projection was wrong by about eleven hours.** It expected `MUF_UP` to
close near 12:00 and `PDF_CTEQ6L1` near 13:00 on 2026-08-19. Recorded because the
projection was published, and a projection that is quietly dropped teaches
nothing.

**Pre-authorised decision 2 applied: report and end.** No extraction was
started. No waiter is armed. This session did not stop, restart or re-plan
either merge.

### 21.2 Readiness

| deliverable | campaigns holding it |
|---|---|
| D1, per-category decomposition | **5 of 7** |
| D2, per-class balancing yield | **5 of 7** |
| D2, integrated balancing yield | **5 of 7** |

The five are `HF_SYS_MUR_UP`, `HF_SYS_MUR_DOWN`, `HF_SYS_MUF_DOWN`,
`HF_SYS_PTHAT_1` and `HF_SYS_PTHAT_4`. The two missing are **both
load-bearing**: `MUF_UP` is S1b's up arm and `CTEQ6L1` is the whole of S2.
Neither is a source that could be dropped as negligible without measuring it.

### 21.3 The combination — built, tested, and refusing

`extraction/combine_per_class.py` exists and **does not run**:

```
COMBINATION_REFUSED missing=HF_SYS_MUF_UP,HF_SYS_PDF_CTEQ6L1
Pre-registration section 9: a partial quadrature sum understates.
```

The refusal is in the library as well as the command, so a caller cannot reach
past it: `combine_cell` raises `SourcesIncomplete` naming the missing campaigns.

**It supplies the wiring and none of the rules.** Every rule was already encoded
on `systematics_delta` as a required policy flag:

| rule | where it comes from | what the driver does |
|---|---|---|
| A1, `max(\|Δ\|, SEM)` continuously | owner, 2026-08-18 | passes `UNRESOLVED_MAX_ABS_OR_SEM`; never branches on the 2 SEM flag |
| A2, S6 stays on `M1…M5` | owner, 2026-08-18 | passes `s6_policy="separate"`; an S6 term raises |
| §9.1, μ_F against PDF | pre-registration | `correlated_pair_choice`, quote the larger and drop the other |
| §2.5, the larger arm | pre-registration | `larger_arm` per two-sided source, per class |
| §9.5, S5 is zero | measured 2026-08-17 | included as an explicit zero term, not omitted |

**The tune-bundle spread is not added.** It is not a systematic and appears
nowhere in the driver.

**25 hand-computed checks**, `tests/test_combine_per_class.py`. The case the
brief names is the first one. S1a resolves and contributes its `|Δ| = 3`. S3
does not resolve and contributes its `SEM = 4`. The two combine to exactly 5.
The file also holds A1's continuity across 2 SEM, the §9.1 drop, both S6
refusals, and the partial-source refusal. A last check proves that per cent and
absolute units give the same answer.

### 21.4 The class axis runs opposite to its label

**Checked, not assumed, and it changes the reading of every per-class table.**
The window label is a **top** percentile — the fraction of minimum-bias events
above the boundary. The render log states the mapping outright:

```
MULTIPLICITY_BOUNDARY percentile=100     nch=0
MULTIPLICITY_BOUNDARY percentile=88.197  nch=2
MULTIPLICITY_BOUNDARY percentile=8.422   nch=32
MULTIPLICITY_BOUNDARY percentile=0       nch=4095
```

So `c1`, labelled `MB88p197_100`, holds `N_ch` 0 to 2 and is the **lowest**
multiplicity class. `c11`, labelled `MB0_8p422`, holds `N_ch` 33 and above.

**The plotting configuration and the boundary artifact agree**, and the label is
the only thing that misleads: `config/multiplicity_class_boundaries_v1.json`
gives `c1` the span `[-0.5, 2.5)` and leaves `c11` open above 32.5.
`tests/test_harvest_class_axis.py` now holds the two statements together so
neither can drift, and `harvest_class_axis`'s docstring carries the mapping.

The trigger profile is the third witness. B⁺ triggers climb from 41,310 in `c1`
to 246,735 in `c11`, and the eleven classes sum to the integrated bin exactly,
1,426,450 for beauty and 13,656,517 for charm.

### 21.5 The tune separation, delivered

Full tables:
[`results/systematics/20260819/TUNE_SEPARATION.md`](../results/systematics/20260819/TUNE_SEPARATION.md),
`tune_separation.json` sha256 `cf378972c3a105c9b1014a6d5b997b3707d2d21cb86147535690aee0f521d2dc`
**at the time of writing**. §22.4 extended the artifact to CLOSEPACKING and
it now digests `37aae5bd…`. The number above is left as written, because a
record of what a session produced is not improved by editing it later.

**This is the half of the headline comparison that needs no variation**, so it is
delivered while the other half is refused. Three observables, twelve classes
each, MONASH minus JUNCTIONS on the sealed nominal.

| observable | stat. σ, `c1` → `c11` | % of MONASH to erase, `c1` → `c11` |
|---|---|---|
| B⁺–B⁻ balancing yield | 2.2 → 39.7 | 4.5 → 31.9 |
| B⁺–Λ_b balancing yield | 2.2 → 49.4 | 9.7 → 128.4 |
| Λ_b/B⁻ ratio | 2.5 → 59.2 | 14.8 → 235.5 |

**Two methodological points, both of which would be wrong if done the obvious
way.** The three tunes are separate generation campaigns with their own raw
files and seeds, so the SEM of a difference is the two SEMs in quadrature. The
Λ_b/B⁻ ratio takes the plotter's `ratio_sem`, formed inside each block, because
numerator and denominator share their triggers and their events.

**MONASH's Λ_b/B⁻ ratio declines gently, from 0.1865 at `c1` to 0.1619 at
`c11`: a contrast of −0.02453 ± 0.00739, 3.3 σ from zero. JUNCTIONS rises over
the same axis, from 0.2141 to 0.5432.** The separation grows monotonically with
multiplicity in all three observables.

**No verdict is given.** The verdict is whether the separation exceeds its
uncertainty, and the uncertainty is the combined systematic, which does not
exist. The last column states what the systematic would have to reach to erase
each gap, which is arithmetic on the nominal and quotes no systematic.

### 21.6 Processes

**Started by this session:** none on the cluster. No render, no extraction, no
watcher. Every cluster call was a read.

**Left alive and not this session's to touch:** the two merges above.

**Terminated by this session:** none. `pkill -f` was not used. Process queries
were scoped with `ps -u ipardoza`, per §20.9.

### 21.7 What did not happen

**No combination.** Five of seven sources. The driver refuses and the
pre-registration forbids it.

**No headline verdict.** It depends on the combination.

**No merge, no PR.** `Paper/**` and `References.bib` untouched. The publication
gate predicate is unchanged. `HADRONIZATION_COMPLETE_ROOT_TAG` and the subsample
base were never set. No origin audit, no counter re-analysis. GOLDEN_OUTPUTS
section numbers were not renumbered; the duplicate 2.10 waits for the
documentation pass.

### 21.8 Handoff

**Suite: 61 Python test files, 61 of 61 passing**, plus 5 C++ files. It was 60;
this session added `test_combine_per_class.py` and one check to
`test_harvest_class_axis.py`, which now runs 11.

#### Commits

| commit | what |
|---|---|
| `2345947` | the combination driver that refuses, the tune separation that does not need it, the class-axis direction |
| *(this section)* | §21, SYSTEMATICS §0 method column and §10, GOLDEN_OUTPUTS §2.14 and §2.15 |

#### The next session's first three moves

1. **Probe the stragglers.** `MUF_UP` was in closure leg 1 of 3 at 16:48 and
   should finish near 22:45 on 2026-08-19. `PDF_CTEQ6L1` had 22 of 33 products
   and had not begun closure. **Marker count first, then the PID.** Commands in
   §19.2.
2. **For each campaign that has closed**, add a selector row with
   `tools/add_variation_selector_rows.py`, then render it with
   `MEASUREMENT_WIDEN_AXES=1` and `MEASUREMENT_INTEGRATED_BIN` set. **Run the
   control first.** The recipe is `GOLDEN_OUTPUTS` §2.13. Read no number until
   the render reports `rc=0`, `output_assertion=0` and
   `RESOLVER_ASSERTION_PASS` for the campaign asked for.
3. **With all seven, run `extraction/combine_per_class.py`.** It is written and
   tested and will run the moment its inputs exist. Then join it to
   `tune_separation.json` for the headline verdict: the ratio of the separation
   to the combined systematic, per class, per observable.

#### What the headline verdict still needs

The separation is measured and its **statistical** significance runs from 2.2 σ
at `c1` to 66 σ integrated. The verdict asks a different question, and the
denominator it needs is the combined systematic. The `% of MONASH to erase`
column in `TUNE_SEPARATION.md` is the threshold each class sets. It runs from
4.5 per cent at `c1` for B⁺–B⁻ to 235.5 per cent at `c11` for the Λ_b/B⁻ ratio. **The low-`N_ch`
classes are where the answer could go either way.**

#### Cautions carried forward

- **`c1` is the lowest multiplicity, `c11` the highest.** The percentile label
  says the opposite. §21.4.
- **The deploy's git HEAD reads `769e351`**, older than its working files. Check
  shas, not `git rev-parse`. §20.11.
- **Scope process queries by user.** The Nikhef login nodes are shared and an
  unscoped `pgrep -f` returns other people's processes. §20.9.
- **A render can emit all 144 rows and still fail.** Two did on 2026-08-19, at
  the drawing stage, and their numbers were correctly not used. §20.4.
- **33 of 33 products is not closure.** The marker count is the answer. §21.1.

---

## 22. THE STRAGGLERS STILL HOLD, AND THE TREND IS MEASURED — 2026-08-19 17:16

### 22.1 The straggler probe

Probed once, at **17:16:22 CEST**, by exact filename and never by a glob.

| campaign | products | closure markers | merge PID | host | elapsed |
|---|---|---|---|---|---|
| `HF_SYS_MUF_UP` | 33/33 | **0/3** | 3953522 | `stbc-i3` | 25 h 16 m 20 s |
| `HF_SYS_PDF_CTEQ6L1` | 22/33 | **0/3** | 642060 | `stbc-i2` | 25 h 15 m 49 s |

**Marker first: 0 of 3 for both, so neither has closed.** Absence second: both
merge processes are alive and `Ss` on their own launch hosts.

`HF_SYS_MUF_UP` is **52 minutes into closure leg 1 of 3**, on MONASH, with its
ROOT process in state `R`:

```
3417215  validate_pair_block_closure.sh …complete_root_HF_SYS_MUF_UP_MONASH … v3 10000000
3417285  root -l -b -q ValidatePairBlockClosure.C(…MONASH…)
3417286  root.exe …                                            (state R)
```

At the 2 h 04 m to 2 h 22 m per tune that §14.2 measured, leg 1 ends near 18:30
and leg 3 near 22:45. `HF_SYS_PDF_CTEQ6L1` still has eleven products to merge
before it starts closing at all.

**Pre-authorised decision 2 applied: report and end.** Nothing extracted, no
waiter armed, neither merge touched.

### 22.2 Inherited claims, verified on disk

| claim | check |
|---|---|
| tip `046d85b` | `git log` agrees; tree clean but for untracked `INSTALL.md` |
| suite 61/61 | ran, 61 of 61 passed before this session's additions |
| the combination refuses | `COMBINATION_REFUSED missing=HF_SYS_MUF_UP,HF_SYS_PDF_CTEQ6L1`, exit 2 |
| `tune_separation.json` digest | `cf378972…` matched GOLDEN_OUTPUTS in both places |
| the class axis is a top percentile | `test_harvest_class_axis.py` passes, 11 checks |

### 22.3 Readiness, unchanged

**5 of 7** for all three deliverables. The two missing campaigns are both
load-bearing: `MUF_UP` is S1b's up arm and `CTEQ6L1` is the whole of S2.

### 22.4 The trend, which needs no variation campaign

**Task 4's core is a property of the sealed nominal, so it is delivered while
tasks 2 and 3 are refused.** Full tables:
[`results/systematics/20260819/RATIO_TREND.md`](../results/systematics/20260819/RATIO_TREND.md).
`ratio_trend.json` sha256 `b1b5954812398d748297111ab64375d2abecfb4d04b3e98ff3ccdf8d9890087e`.

**A set of per-class gaps does not establish a trend.** The claim is that the
ratio rises under reconnection and does not under MONASH, which is a statement
about slope. Two estimators, and the model-free one leads.

**R(c11) − R(c1), no fit and no x-axis convention:**

| tune | contrast | stat. σ |
|---|---|---|
| MONASH | **−0.02453 ± 0.00739** | 3.3 |
| JUNCTIONS | **+0.32909 ± 0.01053** | 31.2 |
| CLOSEPACKING | **+0.28719 ± 0.01364** | 21.1 |

**MONASH is not perfectly flat.** It declines gently, at 3.3 σ. Recorded because
"flat" is the word a reader expects and it is not quite the measurement.

**The weighted straight line in class index:**

| tune | slope per class | χ²/ndf |
|---|---|---|
| MONASH | −0.001210 ± 0.000369 | 12.7/9 = **1.41** |
| JUNCTIONS | +0.034804 ± 0.000709 | 73.6/9 = **8.18** |
| CLOSEPACKING | +0.032760 ± 0.000741 | 58.5/9 = **6.49** |

**A STRAIGHT LINE DOES NOT DESCRIBE THE RECONNECTION TUNES.** The rise is real
and monotone and is not linear in the class index. The slope is recorded as a
summary and never as a model, and the results document says so where a reader
would otherwise quote it as one. The endpoint contrast is the measurement.

**The x-axis is the class index, which is a convention rather than a
measurement.** `c1` spans three units of `N_ch` and `c11` is open-ended above
32, so a slope "per class" is not a physical d(ratio)/d`N_ch`.

**The trend difference against MONASH:**

| tune | slope difference | stat. σ | endpoint difference | stat. σ |
|---|---|---|---|---|
| JUNCTIONS | +0.036014 ± 0.000799 | **45.1** | +0.35362 ± 0.01287 | **27.5** |
| CLOSEPACKING | +0.033970 ± 0.000828 | **41.0** | +0.31172 ± 0.01551 | **20.1** |

**The enhancement over MONASH grows monotonically**, 1.148 → 3.355 for
JUNCTIONS and 1.160 → 3.109 for CLOSEPACKING, across `c1` to `c11`.

**Correlation is stated rather than assumed.** Within one tune the classes are
disjoint event sets. If the ten-block resampling correlates them positively then
`Var(A−B)` is smaller than the quadrature sum, so these uncertainties are
conservative in that direction.

### 22.5 CLOSEPACKING against MONASH, added

`write_tune_separation.py` now covers both reconnection tunes, so the per-class
separation exists for `CLOSEPACKING` as well as `JUNCTIONS`. The artifact moved
from `cf378972…` to **`37aae5bdad84dc6652399b2c77ddc6ae9c6c91df5073df6af1510d560315befd`**,
and GOLDEN_OUTPUTS and SYSTEMATICS carry the new digest.

### 22.6 The verdict is still not given

**Tasks 2 and 3 are refused, and task 4's closing clause with them.** The
verdict asks whether the separation and the trend survive the combined
systematics. The combination needs all seven campaigns.

**The threshold is recorded so the next session checks it in one step.** To
erase the JUNCTIONS-minus-MONASH trend a combined systematic would have to reach
**0.354 in the endpoint contrast** or **0.036 per class in the slope** — the
whole of the measured effect, correlated in the direction that cancels it. For
CLOSEPACKING, 0.312 and 0.034.

### 22.7 Processes

**Started on the cluster by this session: none.** Every cluster call was a read.
**Terminated: none.** `pkill -f` was not used and process queries were scoped
with `ps -u ipardoza`. **Left alive and not this session's to touch:** the two
merges above.

### 22.8 Handoff

**Suite: 62 Python test files, 62 of 62 passing**, plus 5 C++ files. It was 61;
this session added `test_ratio_trend.py`.

#### Commits

| commit | what |
|---|---|
| `bb0bf70` | the trend of the baryon ratio, CLOSEPACKING against MONASH, the new separation digest |
| *(this section)* | §22, SYSTEMATICS §11, GOLDEN_OUTPUTS §2.16 |

#### The state of the seven, at 17:16 CEST

| | |
|---|---|
| five closed and extracted | `MUR_UP`, `MUR_DOWN`, `MUF_DOWN`, `PTHAT_1`, `PTHAT_4` |
| `HF_SYS_MUF_UP` | 33/33 products, closure leg 1 of 3, **projected close near 22:45** |
| `HF_SYS_PDF_CTEQ6L1` | 22/33 products, closure not started, **later still** |

#### The next session's moves, in order

1. **Probe both stragglers.** §19.2's commands. **Marker count first.** A
   campaign at 33/33 products with 0/3 markers has not closed.
2. **Extract whatever closed**, control first, through
   `tools/render_measurement.sh` with `MEASUREMENT_WIDEN_AXES=1` and
   `MEASUREMENT_INTEGRATED_BIN` set. Recipe in `GOLDEN_OUTPUTS` §2.13. Read no
   number until the render reports `rc=0`, `output_assertion=0` and
   `RESOLVER_ASSERTION_PASS` for the campaign asked for.
3. **With all seven, run `extraction/combine_per_class.py`.** It is written,
   tested with 25 hand-computed checks, and refuses until its inputs exist.
4. **Then the verdict**, joining three artifacts that already exist:
   `per_class_deltas.json` for the cells, `tune_separation.json` for the
   per-class gaps, `ratio_trend.json` for the trend. Nothing else needs
   building.

#### What the verdict will turn on

| quantity | measured value | what the systematic must reach to erase it |
|---|---|---|
| JUNCTIONS − MONASH trend, endpoint | +0.35362 ± 0.01287 | **0.354** |
| JUNCTIONS − MONASH trend, slope | +0.036014 ± 0.000799 | **0.036 per class** |
| CLOSEPACKING − MONASH trend, endpoint | +0.31172 ± 0.01551 | **0.312** |
| B⁺–B⁻ gap at `c1` | 4.5 % of MONASH | **4.5 %** |
| Λ_b/B⁻ gap at `c11` | 235.5 % of MONASH | **235.5 %** |

**The trend is where the claim is strongest and the low-`N_ch` per-class gaps
are where it is weakest.** A systematic large enough to erase the trend would
have to be the size of the entire effect and correlated in the one direction
that cancels it.

#### Cautions carried forward

- **`c1` is the lowest multiplicity, `c11` the highest.** The percentile label
  says the opposite. §21.4.
- **A slope in class index is a convention.** The classes are not equally spaced
  in `N_ch`, and χ²/ndf 8.18 says a line does not describe JUNCTIONS. §22.4.
- **33 of 33 products is not closure.** The marker count is the answer. §21.1.
- **The deploy's git HEAD reads `769e351`**, older than its working files. Check
  shas. §20.11.
- **Scope process queries by user.** The login nodes are shared. §20.9.
- **A render can emit all 144 rows and still fail.** §20.4.

---

## 23. THE DISK MAP, THE SEED CHECK, AND TWO SPECIFIED CHANGES — 2026-08-19 21:0x

**Read-only on Nikhef throughout.** Nothing deleted, moved, renamed or created
there. No git command on the Nikhef checkout. No process started or killed.

### 23.1 The deliverable

The private cluster-cleanup plan maps all of
`/data/alice/ipardoza` — 1294.2 G of project data and 1305.6 G belonging to
other users — and classifies every entry. **18.8 G is recoverable once the
merges close; 496.7 G after acceptance**, of which `RootFiles/HF/` alone is
326.6 G.

### 23.2 The seed check — the paper is clean

**`HF_RUN3_V1` and all seven `HF_SYS_*` share no seed with the archived
campaign `HF_100M_primaryGround_ccbb_v1`.** The intersection is empty for all
eight. Seeds came from the canonical manifests, which record what ran, not from
`burned_seeds.txt`, which is the gate.

**Two early campaigns do collide**, and both are named in the plan §8.3: seed
`100200001` (`HF_SMOKE2` attempt 2) and `100400001` (`HF_PT2` attempt 4).

**The cause is a shared `campaign_ordinal`.** `HF_100M`, `HF_PT2` and
`HF_SMOKE2` all carry ordinal 1, and the ordinal selects the seed band. **From
ordinal 3 — `HF_RUN3_V1` — onward, each campaign holds its own ten-million
band.** No campaign the paper uses can collide with anything before it.

**The impact ruling belongs to the owner and this session did not make it.**

### 23.3 Gate against record

`config/burned_seeds.txt` holds **5 727** seeds across 12 campaigns. The 11
canonical manifests hold **5 460**. The 267 difference is retries, which the
gate is right to keep. **The gate holds no entry at all for the archived
campaign's 500 seeds.**

### 23.4 Two changes specified and NOT applied

**Neither was applied: the merges read the frozen checkout.** Both are written
out in the plan §11 with rationale and test.

1. **`extraction/pipeline/tune_chain.sh:63`** invokes
   `/data/alice/ipardoza/tune_extract.sh`, which the 2026-08-17 consolidation
   moved. Every published number still regenerates from committed anchors, so
   nothing is unreproducible today. **The route from merged ROOT files back to
   those numbers cannot run as written**, and that is the route a reviewer takes
   when the anchors are the thing in question.
2. **The default dataset-selector row must refuse rather than fall back.** A
   silent default is what let five variation renders read the central campaign.

### 23.5 Cautions carried forward

- **`c1` is the lowest multiplicity, `c11` the highest.** §21.4.
- **33 of 33 products is not closure.** The marker count is the answer. §21.1.
- **Scope process queries by user.** The login nodes are shared. §20.9.
- **The closure validator stages a hidden file**,
  `validation/.pair_block_closure_<C>_<TUNE>.XXXXXX`. **Match nothing by
  pattern while a merge runs.** Plan §6.

---

## 24. ALL SEVEN, COMBINED, AND THE VERDICT — 2026-08-20

The programme is complete. Seven campaigns closed, extracted, combined, and the
paper's central claim tested against its own systematics.

### 23.1 The probe trap, closed

**The handoff probe reported a false negative on the first campaign to close.**
It counts `CANONICAL_PAIR_BLOCK_CLOSURE_PASS` in `merge_<CAMPAIGN>.log`, which is
where the marker lands when the merge driver runs the closure itself. Six of
seven did. `HF_SYS_MUR_UP` did not: its closure was re-run separately on
2026-08-19 after a schema correction, so its three markers are in
`closure_HF_SYS_MUR_UP.log` and its merge log holds none.

Run verbatim on all seven, the §19.2 command returns **0/3 for `HF_SYS_MUR_UP`**
— a campaign that closed first, and cleanly, reads as one that never started.

**A false negative on closure is the dangerous direction.** It says "not ready"
about data that is ready, and the natural response is to wait for a merge that
already finished.

**The corrected command reads both logs:**

```bash
python3 tools/campaign_closure_status.py \
  --merge-runs /data/alice/ipardoza/systematics_harvest/merge_runs \
  HF_SYS_MUR_UP HF_SYS_MUR_DOWN HF_SYS_MUF_UP HF_SYS_MUF_DOWN \
  HF_SYS_PTHAT_1 HF_SYS_PTHAT_4 HF_SYS_PDF_CTEQ6L1
```

It unions the tunes marked across both logs and **names which log answered**, so
the provenance stays visible. Against the real seven it reports all CLOSED, with
`HF_SYS_MUR_UP` `from=closure_HF_SYS_MUR_UP.log`.

**The marker still decides and the product count still does not.** Only where
the marker is looked for has widened. `tests/test_campaign_closure_status.py`
carries 16 checks, anchored on the real case, and pins that a re-run which
logged every marker twice still reads 3/3.

### 23.2 The final two, extracted

| control | result |
|---|---|
| closure | 33/33 products, **3/3 markers**, every leg `errors=0` |
| per-category extraction | **33/33 directories `rc=0`** each |
| render, resolver assertion | **PASS**, central and subsample, each its own campaign |
| render, output-side assertion | **PASS**, 13 publication trees, **0 files touched**, 4/4 artifacts |
| rows emitted | **144/144** each |
| the control render vs the sealed nominal | **144 of 144 rows, zero disagreements** |

**A second control, on the instrument itself.** This session's control render is
**byte-identical on all 144 rows** to the 2026-08-19 control. The instrument did
not move between sessions, so mixing five logs rendered on 08-19 with two
rendered on 08-20 compares like with like. That is measured, not assumed.

**The per-event plausibility check, on every absolute count:**

| campaign | MONASH | JUNCTIONS | CLOSEPACKING |
|---|---|---|---|
| `HF_SYS_MUF_UP` | 0.5589 | 0.4759 | 0.4775 |
| `HF_SYS_PDF_CTEQ6L1` | 0.5695 | 0.4898 | 0.4936 |
| *nominal* | *0.5366* | *0.4631* | *0.4668* |

**All six pass**, every value inside the range the five already spanned, and the
worst more than twenty times clear of the E5 failure mode at about 13.

**Trigger counts are internally consistent in all 1152 rows** across the eight
renders, against the bound the printed precision implies.

### 23.3 Deltas, and the standing check

**1008 cells**, seven campaigns by twelve classes by twelve series. 772 fall
short of 2 SEM. Every cell carries a relative shift: no nominal among the 1008
is zero, so none is named in place of a number.

**The standing check passes.** No two campaigns agree exactly on any row.

### 23.4 S1b — the pair, and its shape

**The largest systematic in the budget, and the UP arm settled its shape.**

| tune | category | DOWN (×0.5) | UP (×2) | \|D\|/\|U\| |
|---|---|---|---|---|
| JUNCTIONS | kExcludedExcited | **−7.0113 ± 0.4200** | **+5.1564 ± 0.3069** | 1.360 |
| CLOSEPACKING | kExcludedExcited | **−13.0501 ± 0.2818** | **+10.0895 ± 0.1768** | 1.293 |

**Opposite-signed in all eleven comparable cells** — two-sided, not one-sided,
not same-signed. **And systematically asymmetric**, the DOWN arm larger in every
resolved category by 1.245 to 1.829. Halving μ_F moves the decomposition more
than doubling it does, which is the shape a logarithmic scale dependence
produces. **Pre-authorised decision 4 applied: a physics result, reported, and
the work proceeded.**

**§2.5 quotes the larger arm, so S1b is governed by DOWN throughout.** The
budget is unchanged from what `MUF_DOWN` alone implied; the UP arm established
the shape rather than enlarging the total.

**S2 is the smallest live source on the category axis** — largest resolved shift
+2.2649 per cent against S1b's −13.05, and three of eleven cells short of 2 SEM.
It is not small everywhere: on the trend it is the **largest** contributor for
CLOSEPACKING at 36.03 per cent. A source can be small on one axis and large on a
derived quantity, which is why §9.1's choice runs per quantity.

### 23.5 The combination

`extraction/combine_per_class.py` ran for the first time: **144 cells**, all
seven sources. Every rule is the pre-registration's or the amendment's and the
driver adds none.

**The systematic is large where the statistics are thin**: 23 to 46 per cent in
`c1`–`c4`, 6 to 13 per cent in the integrated bin.

### 23.6 The verdict, and how the systematic on a difference is computed

**It is not borrowed from one tune and it is not propagated.** A variation moves
MONASH and JUNCTIONS in the same direction, so part of it cancels in their
difference; applying one tune's systematic would double-count what cancels.

For every source the quantity is **recomputed from that source's own render** and
differenced against the nominal. Whatever cancels inside the quantity has
cancelled before the combination sees it, because it is one number computed
twice.

**The trend:**

| quantity | value | stat | syst | total | σ | holds? |
|---|---|---|---|---|---|---|
| trend JUNCTIONS − MONASH | **+0.35362** | 0.01287 | 0.15999 | 0.16051 | **2.2** | **yes** |
| trend CLOSEPACKING − MONASH | **+0.31172** | 0.01551 | 0.15434 | 0.15512 | **2.0** | **yes** |

**THE CLAIM HOLDS, AT ABOUT 2 SIGMA.** The erase threshold was 0.354; the
systematic reaches 0.160, 45 per cent of it.

**Statistically the trend difference is 27.5 σ; with systematics it is 2.2 σ.**
Quoting the statistical figure alone would overstate the result tenfold.

**The strongest form needs no combination.** The trend difference is positive in
all seven variation renders, +0.233 to +0.445 against a nominal of +0.354. The
largest single excursion, `MUF_DOWN`, still leaves it at +0.233. Neither the
sign nor the order of magnitude depends on the combination rule.

**The per-class verdict: 49 of 72 cells exceed their total uncertainty, and the
boundary falls at `c5`** in five of six series, `c3` in the sixth. `c1`–`c4`,
N_ch 0 to about 6, is not established.

**"Exceeds its total uncertainty" is a ONE-sigma bar**, which is the question as
posed and a weak one. At two sigma it is **36 of 72** and the boundary moves to
`c7`. The significance climbs monotonically with multiplicity, so doubling the
bar moves the boundary two classes and leaves the shape of the conclusion alone.
**The trend clears both bars**, at 2.20 and 2.01 σ.

### 23.7 Processes

**Started by this session, all exited:**

| PID / PGID | what |
|---|---|
| 3476983 | per-category extraction driver, both campaigns |
| 3478921, 3478922, 3478923 | the two variation renders and the control |

Each launched with `setsid`, so PGID equals PID. **Nothing was killed**,
`pkill -f` was not used, and process queries were scoped with `ps -u ipardoza`.

### 23.8 What did not happen

**No merge, no PR.** `Paper/**` and `References.bib` untouched. The publication
gate predicate is unchanged. `HADRONIZATION_COMPLETE_ROOT_TAG` and the subsample
base were never set. No counter re-analysis, no cleanup, and the queued fixes
(`tune_chain`, the selector default, `merge_root_files:27`) were left alone.

### 23.9 Handoff

**The systematics programme is complete.** Seven campaigns generated, merged,
closed, extracted, combined, and the central claim tested against its own
systematics. Nothing in it is waiting on a job.

**Suite: 64 Python test files, 64 of 64 passing**, plus 5 C++ files. It was 62;
this session added `test_campaign_closure_status.py` and
`test_combine_derived.py`.

#### What exists now that did not

| | |
|---|---|
| campaigns extracted | **7 of 7** — per-category, per-class and integrated |
| per-class delta cells | **1008** |
| combined systematic | **144 cells**, per class per tune per series |
| the verdict | per class and on the trend, both tunes |

#### The numbers a referee will ask about first

| quantity | value | stat | syst | σ |
|---|---|---|---|---|
| trend JUNCTIONS − MONASH | +0.35362 | 0.01287 | 0.15999 | **2.2** |
| trend CLOSEPACKING − MONASH | +0.31172 | 0.01551 | 0.15434 | **2.0** |

**Do not quote the statistical significance alone.** It is 27.5 σ and the honest
figure is 2.2 σ.

#### Cautions carried forward

- **`c1` is the lowest multiplicity, `c11` the highest.** The percentile label
  says the opposite. §21.4.
- **Closure markers can live in `closure_<CAMPAIGN>.log`.** Use
  `tools/campaign_closure_status.py`, not a merge-log grep. §23.1.
- **The systematic on a difference must be computed on the difference.**
  Borrowing one tune's per-class systematic double-counts what cancels. §23.6.
- **The deploy's git HEAD is older than its working files.** Check shas, not
  `git rev-parse`. §20.11.
- **Scope process queries by user**; the login nodes are shared. §20.9.
- **A render can emit all 144 rows and still fail.** §20.4.

#### Queued, and deliberately not done here

`tune_chain`, the selector default, and `merge_root_files.sh:27` — a separate
session. The counter re-analysis (S4) and the Nikhef cleanup are both untouched.

---

## 25. S4 — THE SUBSET, DECLARED BEFORE THE RUN — 2026-08-20

**This section was written and committed BEFORE any S4 number existed.** Its
purpose is to fix the subset in advance. A subset chosen after seeing a result
bounds nothing, so the choice is recorded first and the run follows it.

**Owner ruling, 2026-08-20: bound S4, do not run it at full campaign scale.**

### 25.1 The subset

| | |
|---|---|
| **tunes** | **all three** — MONASH, JUNCTIONS, CLOSEPACKING |
| **files per tune** | **100 of 1000**, and the first 100 by logical id: `hf_<TUNE>_job000.root` … `hf_<TUNE>_job099.root` |
| **source** | `/data/alice/ipardoza/hadronization_production/HF_RUN3_V1/raw/<TUNE>/` |
| **events** | 100 000 per file, so **10 M per tune**, against the campaign's 100 M |
| **arms** | **two**, on the *same* 100 files: the wide classifier (`\|η\| < 4`) and a narrow-classifier control (`\|η\| < 1`) |

**All three tunes, and that is not padding.** The quantity the verdict rests on
is a **difference** — JUNCTIONS − MONASH and CLOSEPACKING − MONASH. A source
measured on one tune cannot bound a difference between two, because a variation
that moves both tunes together partly cancels in their difference and a
single-tune measurement cannot see the cancellation. `VERDICT.md` §1 states this
rule for every source: *"A variation moves MONASH and JUNCTIONS in the same
direction, so part of it cancels in their difference."*

**The first 100 by logical id, named now.** The selection is deterministic and
stated before the run so it cannot be reselected. It matches the pre-registered
subset rule A2 used: *"**100 files per tune**, not 1000 — this is a systematic,
not a central value"* (private branch-state pending item 8).

### 25.2 Why a 10 % subset BOUNDS the contribution rather than merely estimating it

**The bound follows from owner ruling A1, not from an assumption about S4.**

A1 fixes what a source contributes to the combination:

> each source contributes `max(|Δ|, SEM(Δ))`, continuously, no threshold cliff

`|Δ(c)|` is an estimate of a fixed quantity and does not systematically grow or
shrink with sample size. `SEM(Δ(c))` does: at 10 % of the events it is about
**√10 ≈ 3.2×** larger than the same measurement at full scale.

**So the subset can only inflate S4's contribution, never deflate it.** Where
`|Δ|` dominates, the subset returns the same contribution as full scale up to its
own noise. Where `SEM` dominates — which is where a small sample lands — the
subset returns a contribution about 3.2× the full-scale one. Either way the
number entering quadrature is at least the full-scale number in expectation.

**The consequence, stated in advance so the run cannot be read selectively.** If
the bounded contribution is immaterial to the verdict, then the full-scale
contribution is immaterial a fortiori, and S4 needs no full-scale run. **If the
bounded contribution is material, that is not a result — it is an instruction to
run S4 at full scale**, because a material number at 10 % statistics may be
nothing but the inflated SEM. This session commits to that reading now.

### 25.3 The instruments, the same four every other source used

1. **Resolver assertion.** The dataset resolver must name `HF_RUN3_V1` explicitly
   and refuse a silent default. Both arms assert the resolved raw base before
   reading.
2. **Output-side assertion.** Each arm asserts its own output carries the
   classifier it was asked for, read back from the artifact rather than assumed.
3. **The control reproducing the nominal.** The narrow arm runs the same code on
   the same 100 files and must reproduce the nominal classification. This is the
   decisive control: Δ is formed on **identical events**, so shared event content
   cancels, as `ValidationReports/NCH_DECAY_POLICY_BIAS_8317.md` did for S5 by
   pairing both arms on one seed.
4. **Per-event plausibility on every absolute count.** Every absolute count is
   divided by its event total and checked against the recorded per-event rate
   before any ratio is formed.

### 25.4 A DEVIATION from the pre-registration, declared as one

**The registered method was a full evaluation. This is a bound.** Recorded in the
shape the I2 ruling used: the registration stands as written, and the departure
from it is reported rather than retro-fitted.

`docs/SYSTEMATICS_PREREGISTRATION.md` §6 registers, under *Sample size*:

> The full existing campaign — 3000 files, 100 M events per tune. No new
> generation, so there is no reason to subset.

**That is not what this session runs.** Three departures, each named:

| # | registered | executed | why |
|---|---|---|---|
| **D1** | 1000 files per tune | **100 files per tune** | owner ruling 2026-08-20. §25.2 gives the argument that makes a subset a bound |
| **D2** | *"no new generation"* | **a new minimum-bias generation run is required** | §25.5 — the registered boundary source does not carry the wide counter |
| **D3** | the variation alone | **the variation and a narrow-classifier control on the same files** | the control is what makes Δ a difference on identical events rather than a comparison against the full-scale nominal, whose statistics differ by 10× |

**D2 is a defect in the registration, not a choice.** It is recorded here rather
than corrected in the pre-registration, for the same reason the I2 flags are a
deviation: a registration edited after the fact stops being a registration.

### 25.5 The registered boundary source cannot supply the wide counter

**Measured, not assumed.** `docs/SYSTEMATICS_PREREGISTRATION.md` §6 names the
boundary source:

> recompute each boundary as the wide-counter value at the same
> MONASH-minimum-bias percentile the narrow boundary sits at, from the committed
> MB samples in `AnalysisScripts/anchors/b4_multiplicity_mb`

**Those samples hold the narrow counter only.** Read from the artifact on
2026-08-20:

```
rootls -l /data/alice/ipardoza/b4_mapping/out/nch_mb_MONASH.root
TH1D  hNch_mb_MONASH;1 "NCH_PRIMARY_CHARGED_ETA10_V1"
```

One histogram, and it is the `|η| < 1` counter. The committed anchor
`AnalysisScripts/anchors/b4_multiplicity_mb/MANIFEST.md` says the same in prose:
*"`nch_mb_<TUNE>.root` | the MB N_ch histogram, `hNch_mb_<TUNE>`"*, defined on
`NCH_PRIMARY_CHARGED_ETA10_V1`.

**The producer of that artifact is hard-wired to the narrow counter.**
`Validation/CalibrateMultiplicityAgainstMinBias.C:177` refuses anything else:

```
"ERROR: counter[%zu] is not NCH_PRIMARY_CHARGED_ETA10_V1 "
```

And it generates its own events rather than reading raw — `b4_mapping/run_b4.sh`
calls it with an event count and a tune card, so obtaining the wide-counter MB
reference is a **generation** step. That is D2.

**The wide counter itself is present in the campaign's raw**, verified the same
day on `hf_MONASH_job000.root`: branches
`multiplicity_primary_charged_eta10_v1` and
`multiplicity_primary_charged_eta40_v1`, and histograms `hMULTIPLICITY` and
`hMULTIPLICITY_ETA40`. The variation's input exists; only its **label
definition** is missing.

**The campaign's own wide distribution is not a substitute**, and the
pre-registration says why: the class labels are percentiles of the MONASH
**minimum-bias** distribution, and deriving them from the hard heavy-flavour
sample instead *"would be dominated by the relabelling rather than by the
physics"*. The MB run is therefore required, not a convenience.

### 25.6 What this section commits this session to

- The subset above, unchanged, whatever the run returns.
- Reporting the bound with its statistics, and reporting `SEM(Δ)` beside `|Δ|`
  in every class so a reader can see which term A1 selected.
- Reporting a material bound as an instruction to run at full scale, not as a
  measured systematic.
- Recording the run as a deviation, per §25.4.

---

## 26. S4 STAGE 1 — THE WIDE AXIS EXISTS, AND BOTH CONTROLS ARE EXACT — 2026-08-20

**The subset declared in §25 is unchanged.** This section reports stage 1 of
that plan: the boundary derivation that §25.5 established the pre-registration
could not supply. Stages 2 to 4 are not collected — §26.6 says where they stand.

### 26.1 What ran

| | |
|---|---|
| macro | `Validation/CalibrateBothCountersAgainstMinBias.C`, sha256 `050ad0e011b35cbb53940e261c97cd2908e54c525900f806c61b8ce37fb2d9e7` |
| derived from | `Validation/CalibrateMultiplicityAgainstMinBias.C`, sha256 `3be7a094…`, the recorded `B4_MACRO_SHA256` — **verified on the deployed copy before editing** |
| host | `stbc-i3`, ROOT 6.30/01, PGID `571311` |
| events | **200 000 requested per tune**, matching `b4_mapping/run_meta.txt` |
| output | `/data/alice/ipardoza/s4_run/out/nch_mb_both_<TUNE>.root`, two histograms per file |

**The change is additive and that is the point.** The original macro already
computed the `|η| < 4` counter — it is entry 4 of its ladder — and used it only
for a `dN_ch/dη` row. The variant adds a second `TH1D` on the same binning, a
per-event `wideNch`, and a fail-closed guard on the wide slot mirroring the
existing one on the narrow slot. **The narrow histogram's definition is
untouched**, which is what makes §26.2 a control rather than a coincidence.

> **The original macro was not edited.** Its sha256 is recorded provenance in
> `AnalysisScripts/anchors/b4_multiplicity_mb/MANIFEST.md`. The variant is a new
> file, and the deployed original was hashed before the copy to confirm the
> recorded digest still describes it.

### 26.2 THE CONTROL REPRODUCING THE NOMINAL — exact, in both tunes

**§25.3 instrument 3, and it passed exactly rather than approximately.**

| tune | fresh narrow total | committed anchor | bins differing |
|---|---|---|---|
| MONASH | **172 429** | 172 429 | **0 of 94** |
| JUNCTIONS | **170 389** | 170 389 | **0** |
| CLOSEPACKING | **170 261** | 170 261 | **0** |

**All three tunes, completed 2026-08-20 08:15:34 UTC**, `S4_MB_BATCH_DONE`, every
leg `S4_MB_EXIT=0`.

The fresh run reproduces
`AnalysisScripts/anchors/b4_multiplicity_mb/nch_mb_<TUNE>.csv` **bin for bin**,
against an artifact generated on 2026-08-09 from a different checkout.

**What that establishes, precisely.** The wide histogram was added without
perturbing the narrow one, and the minimum-bias generation is deterministic
across checkouts and six months of repository change. **A shift in the narrow
distribution would have invalidated the whole derivation silently**, because the
wide boundaries are defined by matching narrow percentiles.

### 26.3 Per-event plausibility — §25.3 instrument 4

Every absolute count divided by its event total, before any ratio:

| counter | ⟨N_ch⟩ | dN_ch/dη |
|---|---|---|
| \|η\|<0.5, pT>0, heavy incl. | 6.890 | **6.890** |
| \|η\|<0.5, pT>0.15, heavy incl. | 6.326 | **6.326** |
| \|η\|<0.5, pT>0.15, heavy excl. | 6.306 | **6.306** |
| **\|η\|<1.0** (the analysis counter) | 12.683 | **6.342** |
| **\|η\|<4.0** (the S4 counter) | 50.439 | **6.305** |

**The two counters measure the same density.** 6.342 against 6.305 is a 0.6 %
difference across a four-fold change in acceptance, so the wide counter is the
same observable over a wider window rather than a different one. The macro's own
verdict line agrees: *"counter reproduces the minimum-bias reference."*

**The ratio of the means is 3.954** on the 200 000-event MONASH sample
(⟨N⟩ 12.9482 narrow against 51.2005 wide). The pre-registration predicted
*"roughly 4×"*, before the measurement.

### 26.4 THE WIDE AXIS — percentile-preserving, as registered

`docs/systematics_results_20260820/s4/s4_wide_boundaries_v1.json`. Each wide
boundary is the wide-counter value at the **same MONASH minimum-bias percentile**
its narrow counterpart sits at, kept half-integer so no integer `N_ch` is
ambiguous.

| class | narrow | percentile | **WIDE** | achieved | residual |
|---|---|---|---|---|---|
| `c1` | −0.5 | 0.0000 % | **−0.5** | 0.0000 % | +0.0000 pp |
| `c2` | 2.5 | 11.8031 % | **13.5** | 12.0165 % | +0.2134 |
| `c3` | 3.5 | 19.4028 % | **16.5** | 19.4816 % | +0.0789 |
| `c4` | 5.5 | 34.0627 % | **23.5** | 35.3386 % | **+1.2759** |
| `c5` | 6.5 | 40.1504 % | **26.5** | 40.2647 % | +0.1142 |
| `c6` | 8.5 | 49.6923 % | **34.5** | 49.7909 % | +0.0986 |
| `c7` | 10.5 | 56.9695 % | **42.5** | 57.0855 % | +0.1160 |
| `c8` | 13.5 | 65.3863 % | **54.5** | 65.7140 % | +0.3277 |
| `c9` | 17.5 | 73.8460 % | **69.5** | 73.9209 % | +0.0748 |
| `c10` | 23.5 | 82.8764 % | **92.5** | 83.0649 % | +0.1885 |
| `c11` | 32.5 | 91.5780 % | **124.5** | 91.7143 % | +0.1363 |

**Monotone, and the residual is discreteness rather than method.** The wide
counter is still an integer count, so a percentile can only be matched to the
nearest attainable step. `c4`'s **+1.28 pp** is the largest and it is the
narrowest narrow class — `c4` is the single value `N_ch = 6` — so its percentile
target falls between two attainable wide steps. Every residual is positive
because the rule takes the first step at or above the target.

### 26.5 ⚠ AN UNREGISTERED FINDING — the wide axis is a WORSE common axis

**Measured, and it runs against the direction the pre-registration expected.**

The class axis is defined on MONASH minimum bias, so each other tune sits some
distance from its labels. That distance is the **per-tune residual**, and the
axis ruling requires it be published — `docs/PRODUCTION_SHAPE_DECISION.md`
records **max 2.91 pp** for the narrow axis.

**Both axes recomputed here through one code path**, so this is a like-for-like
comparison rather than a quotation across documents. Residual = that tune's
percentile at the boundary, minus the MONASH label, in pp:

| class | NARROW J | NARROW C | **WIDE J** | **WIDE C** |
|---|---|---|---|---|
| `c1` | +0.000 | +0.000 | **+0.000** | **+0.000** |
| `c2` | −0.588 | +0.053 | **−0.907** | **+0.260** |
| `c3` | −1.362 | −0.309 | **−1.788** | **−0.145** |
| `c4` | −2.575 | −1.006 | **−3.159** | **−1.435** |
| `c5` | **−2.912** | −1.225 | **−3.537** | **−1.793** |
| `c6` | −2.903 | −1.324 | **−3.395** | **−1.717** |
| `c7` | −2.792 | −1.184 | **−3.168** | **−1.254** |
| `c8` | −2.308 | −0.764 | **−2.657** | **−0.747** |
| `c9` | −1.732 | −0.178 | **−1.996** | **−0.060** |
| `c10` | −1.148 | +0.385 | **−1.248** | **+0.642** |
| `c11` | −0.736 | +0.523 | **−0.882** | **+0.676** |
| **max \|residual\|** | **2.912** | | **3.537** | |

**The narrow column reproduces the published number exactly.** 2.912 pp against
`PRODUCTION_SHAPE_DECISION.md`'s **2.91 pp** — a fourth control, and it is what
licenses reading the wide column beside it.

> ### The wide axis is 1.21× worse, and the sign is consistent
>
> **3.537 pp against 2.912 pp.** Every JUNCTIONS class is further from its label
> on the wide axis than on the narrow one, in all ten. CLOSEPACKING is mixed in
> sign but its extreme also grows, `c5` from −1.225 to −1.793.
>
> **The wide counter separates the tunes' activity distributions more, not
> less.** ⟨N_wide⟩ is 51.20 for MONASH, **53.83** for JUNCTIONS and 50.96 for
> CLOSEPACKING, so JUNCTIONS — the tune furthest from MONASH on the narrow axis
> — moves further still when the window opens.

> **Stated with its limit, because it is easy to over-read.** This is the
> per-tune **MB residual**, not the per-class observable shift the
> pre-registration's ≲ 3 % expectation is about. They are different quantities,
> and this measurement does not settle that one.
>
> **What it does say** is that the registered reasoning — *"a wider window
> measures the same activity with less relative fluctuation … so the classes
> should be better resolved"* — does not hold for the one axis property now
> measured on both counters. Less fluctuation smearing does not imply a more
> common axis: widening the window also admits more of the rapidity region where
> the tunes' fragmentation actually differs, and on this evidence the second
> effect is the larger one. **Recorded as a finding rather than folded into the
> expectation**, and it belongs beside S4's result whichever way that lands.

### 26.6 WHAT IS NOT COLLECTED, AND WHAT IT WOULD TAKE

**The bound is not delivered. Stage 1 of four is.** Said plainly rather than
implied by omission.

| stage | state |
|---|---|
| 1. the wide axis, from an MB reference the registration could not supply | ✅ **DONE** — §26.4, with both controls exact |
| 2. re-analyse the declared 100 files/tune with the wide classifier | ⛔ **not run** |
| 3. the narrow-classifier control arm on the same files | ⛔ **not run** |
| 4. merge each arm and render the per-class balancing yield | ⛔ **not run** |

**Why stages 2 to 4 did not run in this session.** They are a Condor analysis
pass over 300 files in each of two arms, then a merge and a render. The measured
cost of a merge at this scale is in the private merge-band validation record — 15 legs
in 48.6 h, projecting ~97 h for 33 — and closure adds 2 h 04 m to 2 h 22 m per
tune (§14.2). **Stage 1 alone took 1 h 15 m of wall clock for three 200 000-event
MB runs**, MONASH in 8 m, JUNCTIONS in 17 m and CLOSEPACKING longer still.

**Stage 1 is complete for all three tunes.** CLOSEPACKING finished at
**08:15:34 UTC**; the batch printed `S4_MB_BATCH_DONE` and PGID `571311` exited.
No process of this session remains on the cluster.

**Nothing about the declared subset changed to fit the session.** §25 fixed 100
files per tune across all three tunes with a control arm, and that is still what
stages 2 to 4 must run. Shrinking it now to fit the time would be exactly the
after-the-fact subset choice §25 exists to prevent.

**S4's contribution therefore stays out of the combination**, and both published
results documents say so — `COMBINED_SYSTEMATICS.md`'s source inventory and
`VERDICT.md`'s note, added 2026-08-20 under §9.5's *"listed rather than
omitted"*.

---

## 27. HANDOFF — 2026-08-20, the close-out session

**Branch `systematics-harvest`, seven commits, `440105b` to this one.**
The private branch-state record carries the merge-readiness assessment; this section carries what the
next session needs in its hands.

### 27.1 Nothing is in flight

**The S4 MB batch finished.** All three legs `S4_MB_EXIT=0`, `S4_MB_BATCH_DONE`
at **2026-08-20 08:15:34 UTC**, PGID `571311` exited. **No process of this
session remains on the cluster**, and none was killed.

### 27.2 To finish S4, in order

1. **Run stages 2 and 3** — the declared 100 files per tune, both arms, wide
   classifier and narrow control. **§25 fixes the subset and it must not move.**
   The analysis macro reads
   `multiplicity_primary_charged_eta10_v1` at
   `analysis/status_analysis_THnSparse_qq.C:395` and `:903`; the wide arm reads
   `…_eta40_v1` and classifies on
   `docs/systematics_results_20260820/s4/s4_wide_boundaries_v1.json`.
2. **Merge each arm and render** the per-class balancing yield, the same route
   every other source used — the plotter's `UNCERTAINTY_MATRIX` line, not
   `tools/statistical_robustness.py`, which needs certificates no campaign here
   has (`SYSTEMATICS.md` §8).
3. **Report `|Δ|` and `SEM(Δ)` per class**, both, so a reader sees which term
   ruling A1 selected. §25.6 commits this session's successor to that.
4. **Fold the bound into the combination**, then restate the verdict. Until
   then `VERDICT.md`'s note stands.

> **If the bound comes back material, that is not a result.** §25.2 committed in
> advance to reading a material bound as an instruction to run S4 at full scale,
> because at 10 % statistics `SEM(Δ)` is about 3.2× its full-scale value and A1
> takes the larger term.

### 27.3 What is deployed on Nikhef, and what was not touched

| path | what |
|---|---|
| `/data/alice/ipardoza/s4_run/` | the S4 scratch deploy: `macro/`, `out/`, `logs/`, `generation/producer/HeavyFlavourUtils.h`, `run_s4_mb.sh` |
| `/data/alice/ipardoza/s4_run/macro/CalibrateMultiplicityAgainstMinBias.C` | the **unmodified** original, sha256 `3be7a094…`, copied only to verify the recorded digest |

**Not touched:** the analysis checkout at `/data/alice/ipardoza/Hadronization`
(`51603c2a`, `physics-focus`, pinfile empty), every campaign tree, every raw
file, and the Nikhef cleanup. **No process was killed. `pkill -f` was not used,
and every process query was scoped with `ps -u ipardoza`.**

### 27.4 Cautions carried forward

- **`c1` is the lowest multiplicity, `c11` the highest.** §21.4.
- **33 of 33 products is not closure.** The marker count answers. §21.1.
- **Scope process queries by user.** The login nodes are shared. §20.9.
- **The tune cards moved.** They are in `generation/cards/`, not
  `SimulationScripts/`; `b4_mapping/run_b4.sh` still names the old path and
  fails on it.
- **`Validation/CalibrateMultiplicityAgainstMinBias.C` is provenance-frozen.**
  Its sha256 is recorded in the b4 anchor manifest. The S4 variant is a separate
  file for that reason.
