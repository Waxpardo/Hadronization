# HF_RUN3_V1 — archived breach partials, 2026-08-09

**34 `.partial.` staging directories moved out of the gate's scan root.**
Nothing deleted. This file is the manifest: it records what moved, from where,
to where, and on what evidence, so the move is reversible by reading it.

| | |
|---|---|
| moved | **34** |
| held back | **0** |
| bytes | **1,034,510,305** (~1.1 GB) |
| from | `…/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/` |
| to | `/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/` |
| slots | `298`–`331`, contiguous |
| tool | `tools/archive_breach_partials.sh --apply` |

---

## Why these directories existed

**Cross-reference: the analysis campaign's checkout-freeze breach.**
`bc37ab7` (ITEM-STOP, the breach), `c2c76f2` (recovery by restored pin),
`docs/handoffs/HANDOFF_20260809_v29.md` and `v30.md` §2.

The analysis wrapper writes `slot_NNN.partial.XXXXXX`, validates it, and
promotes it by atomic rename. The v3 campaign pinned commit `61fe978f`; the
checkout was advanced four times while its 3000 jobs were in flight, and every
job finishing after the first advance **failed its promotion check** — after its
work had already succeeded. 2702 jobs were re-run. These 34 directories are the
staging state of jobs whose promotion failed in exactly that window.

**Slots 298–331 are contiguous**, which is the breach's fingerprint: the submit
is tune-major and the breach interrupted MONASH's block partway through.

**Each partial holds 301 entries against a promoted directory's 302, and the one
it lacks is `analysis_job_metadata.json`** — written last, at promotion. That is
the positive identification of a failed *promotion* rather than a failed *run*.

## Why they could be moved

Each was moved only after its promoted slot was shown to be a complete
replacement:

1. the promoted `slot_NNN` exists,
2. it holds exactly 302 entries,
3. it carries `analysis_job_metadata.json`,
4. its log certifies — exactly one `ONE_PASS_ANALYSIS_SUMMARY`, no
   `ONE_PASS_ANALYSIS_ERROR`,
5. **`ValidatePairDirectory` returned `rc=0 errors=0`** over all 300 pair files
   (cluster `5399125`, one directory per job, one CPU per job).

**All 34 passed all five. `TOTAL=34 MOVED=34 HELD=0`**, matching the
pre-registered dry run exactly. The dry run with partial evidence had correctly
held 13 for `no-validation-evidence`, so the fail-closed path is exercised, not
assumed.

## What was NOT done

**`validate_analysis_outputs.py:373` is unmodified.** Its refusal to run while
any `.partial.` sits in the scan root is correct behaviour and remains. The
material the gate objects to was removed; the objection was not.

---

## The manifest, as emitted by the tool

```
# archive_breach_partials APPLY
# root=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH
# archive=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809
# evidence=/data/alice/ipardoza/gate_runs/validate_34.log
# generated=2026-08-09T20:18:00+02:00
#
MOVE    slot_298.partial.1gPJss          slot=slot_298  files=301   bytes=30511063     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_298.partial.1gPJss to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_298.partial.1gPJss
MOVE    slot_299.partial.imrUhV          slot=slot_299  files=301   bytes=30420200     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_299.partial.imrUhV to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_299.partial.imrUhV
MOVE    slot_300.partial.4kvVuz          slot=slot_300  files=301   bytes=30396924     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_300.partial.4kvVuz to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_300.partial.4kvVuz
MOVE    slot_301.partial.B2W1Dg          slot=slot_301  files=301   bytes=30510849     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_301.partial.B2W1Dg to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_301.partial.B2W1Dg
MOVE    slot_302.partial.E0I11b          slot=slot_302  files=301   bytes=30490040     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_302.partial.E0I11b to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_302.partial.E0I11b
MOVE    slot_303.partial.KaFbmK          slot=slot_303  files=301   bytes=30399704     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_303.partial.KaFbmK to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_303.partial.KaFbmK
MOVE    slot_304.partial.59yalv          slot=slot_304  files=301   bytes=30405531     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_304.partial.59yalv to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_304.partial.59yalv
MOVE    slot_305.partial.21tzJy          slot=slot_305  files=301   bytes=30446234     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_305.partial.21tzJy to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_305.partial.21tzJy
MOVE    slot_306.partial.nPHOpS          slot=slot_306  files=301   bytes=30443701     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_306.partial.nPHOpS to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_306.partial.nPHOpS
MOVE    slot_307.partial.2WqvSM          slot=slot_307  files=301   bytes=30325980     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_307.partial.2WqvSM to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_307.partial.2WqvSM
MOVE    slot_308.partial.eSC3v9          slot=slot_308  files=301   bytes=30376186     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_308.partial.eSC3v9 to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_308.partial.eSC3v9
MOVE    slot_309.partial.fsXxTK          slot=slot_309  files=301   bytes=30477926     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_309.partial.fsXxTK to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_309.partial.fsXxTK
MOVE    slot_310.partial.h8GAHG          slot=slot_310  files=301   bytes=30334517     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_310.partial.h8GAHG to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_310.partial.h8GAHG
MOVE    slot_311.partial.2zjBx9          slot=slot_311  files=301   bytes=30550527     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_311.partial.2zjBx9 to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_311.partial.2zjBx9
MOVE    slot_312.partial.jOTjGx          slot=slot_312  files=301   bytes=30510747     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_312.partial.jOTjGx to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_312.partial.jOTjGx
MOVE    slot_313.partial.csThku          slot=slot_313  files=301   bytes=30362830     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_313.partial.csThku to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_313.partial.csThku
MOVE    slot_314.partial.89KXcC          slot=slot_314  files=301   bytes=30445921     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_314.partial.89KXcC to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_314.partial.89KXcC
MOVE    slot_315.partial.qHq0vD          slot=slot_315  files=301   bytes=30455970     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_315.partial.qHq0vD to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_315.partial.qHq0vD
MOVE    slot_316.partial.ZfElOJ          slot=slot_316  files=301   bytes=30477646     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_316.partial.ZfElOJ to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_316.partial.ZfElOJ
MOVE    slot_317.partial.uwgDSb          slot=slot_317  files=301   bytes=30191411     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_317.partial.uwgDSb to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_317.partial.uwgDSb
MOVE    slot_318.partial.onAUJz          slot=slot_318  files=301   bytes=30469142     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_318.partial.onAUJz to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_318.partial.onAUJz
MOVE    slot_319.partial.F7REEA          slot=slot_319  files=301   bytes=30346530     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_319.partial.F7REEA to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_319.partial.F7REEA
MOVE    slot_320.partial.sNn8oa          slot=slot_320  files=301   bytes=30463868     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_320.partial.sNn8oa to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_320.partial.sNn8oa
MOVE    slot_321.partial.qEQPc0          slot=slot_321  files=301   bytes=30376986     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_321.partial.qEQPc0 to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_321.partial.qEQPc0
MOVE    slot_322.partial.57TTMQ          slot=slot_322  files=301   bytes=30407338     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_322.partial.57TTMQ to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_322.partial.57TTMQ
MOVE    slot_323.partial.n5pntF          slot=slot_323  files=301   bytes=30426012     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_323.partial.n5pntF to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_323.partial.n5pntF
MOVE    slot_324.partial.Wp1Vuf          slot=slot_324  files=301   bytes=30539869     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_324.partial.Wp1Vuf to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_324.partial.Wp1Vuf
MOVE    slot_325.partial.kOM3r6          slot=slot_325  files=301   bytes=30425385     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_325.partial.kOM3r6 to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_325.partial.kOM3r6
MOVE    slot_326.partial.WyFc93          slot=slot_326  files=301   bytes=30547777     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_326.partial.WyFc93 to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_326.partial.WyFc93
MOVE    slot_327.partial.scO6lR          slot=slot_327  files=301   bytes=30284790     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_327.partial.scO6lR to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_327.partial.scO6lR
MOVE    slot_328.partial.03cNnv          slot=slot_328  files=301   bytes=30301321     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_328.partial.03cNnv to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_328.partial.03cNnv
MOVE    slot_329.partial.fuBSNJ          slot=slot_329  files=301   bytes=30470843     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_329.partial.fuBSNJ to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_329.partial.fuBSNJ
MOVE    slot_330.partial.37fpwn          slot=slot_330  files=301   bytes=30502433     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_330.partial.37fpwn to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_330.partial.37fpwn
MOVE    slot_331.partial.kpzkrb          slot=slot_331  files=301   bytes=30414104     from=/data/alice/ipardoza/hadronization_analysis/HF_RUN3_V1/per_job/MONASH/slot_331.partial.kpzkrb to=/data/alice/ipardoza/archive/HF_RUN3_V1_breach_partials_20260809/slot_331.partial.kpzkrb
#
# TOTAL=34 MOVED=34 HELD=0 mode=APPLY
```
