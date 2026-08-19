# Three-tune harvest and re-extraction — 2026-08-13

**The session was briefed to harvest three tunes. It could harvest one, because
the merge had been dead for eight hours when the session opened.** What it did
instead is the part that was never blocked: the I2 recalibration, the MONASH
re-extraction that E5 was waiting on, and the 0.0018 % disposition.

**Two commits, `1640fcb..75da116`. Suite 37/37 throughout** — one test added,
none removed or skipped.

---

## 0. THE FIRST FINDING, AND WHY THE BRIEF SAID TO CHECK THE CLOCK FIRST

The brief said to establish wall-clock time before planning. That instruction
paid for itself immediately.

`stbc-i3` reported **`up 8:07`**. The merge, PID `3675829`, was gone — **killed
by a scheduled-maintenance reboot at 2026-08-12 23:07 CEST**, fifteen minutes
after its last log write, at **15 of 33 promotions**. The three chain watchers
(MONASH, JUNCTIONS, CLOSEPACKING) died with it.

**It was maintenance, not a crash**, and that distinction was checked rather
than assumed: a clean `shutdown` five minutes prior, kernel
`5.14.0-687.26.1 → 687.36.1`, and a matching pattern of reboots at
**Jul 8 23:07, Jul 16 23:09, Aug 12 23:07**. So the node is not unstable, and a
restart is not futile — but *the merge will be interrupted again*, and the only
thing that makes that cheap is that the driver is resumable by construction
(`merge_root_files.sh:95-106` re-validates an existing final directory and never
overwrites it).

> **A local `ps` proved nothing here.** PID 3675829 is a Linux-range PID on a
> remote node; the merge never ran on this machine. Confirming it was dead took
> an ssh, not a local process check.

### What was actually on disk

| tune | central | blocks | chain |
|---|---|---|---|
| **MONASH** | merged | **10 / 10** | complete — closure PASSED, extraction done |
| **JUNCTIONS** | merged | **3 / 10** | started 08-11, never advanced past waiting |
| **CLOSEPACKING** | **not merged** | 0 / 10 | started 08-11, never advanced |

Plus a **1.6 G orphaned stage**, `combined_root_4.partial.l6K9h4`, killed
between its provenance write and its promotion. **Left in place, not deleted** —
it is 1.6 G on a filesystem with 1.1 T free, and deleting another run's retained
stage is not a thing to do unprompted.

### The merge was restarted

Preconditions verified before launching, not after: canonical manifest sha
identical to the original launch record (`fcd96eae…`), checkout tracked-clean and
**unmoved at `43e35be8`**, all four paths present. Relaunched **07:24 CEST**
under `setsid`, log `merge_v4.log`, manifest `manifest_v4.txt`.

At session end it is **alive and working**, still inside the
`validate_analysis_outputs.py` preamble over 3000 directories: `rchar` advancing
**68 MB in 12 s at 37 % CPU**, ~295 GB read. **`rchar`, not atime** — v47 §1
recorded that the atime frontier is invalid on merged outputs and fails as a
silent zero, and this is exactly that situation.

**18 legs remain: JUNCTIONS blocks 4–10, CLOSEPACKING central + 1–10.**

---

## 1. THE I2 RECALIBRATION — executed, and the ruling's arithmetic was wrong

The standing ruling (`GOLDEN_OUTPUTS.md` §2.11a) was implemented exactly as
written: `compare()`'s null is a **required keyword-only argument with no default
anywhere**, I2 passes `mad`, the pinned E4 regression passes `binomial` by name.
Neither caller can inherit a null it did not choose.

**Then the measurement contradicted the ruling's prediction, and the measurement
is what got recorded.**

| | ruling predicted | measured |
|---|---|---|
| σ inflation, anchor case | ~2.2× | **4.399×** (variance 19.4×) |
| Ξ*_c⁺, Σ̄_b⁻ | survive at z ≈ 5.3, 5.0 | **z = +2.83, +2.70 — neither survives** |
| flagged set | "shrinks substantially" | **0 of 88** |

**The error was applying the wrong comparison's overdispersion.** The ~2.2×
comes from `38bf707`'s **block-vs-central** figure, measured on *clean*
comparisons. The anchor-vs-parent comparison is not clean — that is the whole
content of E4 — and its pull distribution really is ~4.4 wide: MAD 4.399, plain
stdev 4.426, IQR/1.349 4.364, three independent estimators agreeing to 1.5 %.

### Zero flags is a property of the instrument, not a clearance

A robust scale estimated **from the sample** absorbs contamination that is
**broad**. The anchor's defect is 30 of 88 bins displaced *together* — the bulk
*is* the defect, so nothing stands out from it. **The MAD null sees localized
failures and is blind to broad ones.**

Every annotation says so, and **the anchor quarantine STANDS** on the grounds it
always rested on: localized, physically large deviations — 16 bins above 2 %, up
to 33 %, almost entirely baryons.

**Operational consequence, recorded in the pre-registration:** I2 and I3 are
**not redundant**. I3's exact block-sum identity is now the only check that can
catch a uniform or sector-wide displacement.

### Two things the ruling did not anticipate, both found by measurement

- **A counting floor.** σ̂ is never allowed below **1.0** for the test statistic.
  The pulls are already in binomial-sigma units, so σ̂ < 1 means *less* dispersed
  than counting statistics permit — impossible for a real sample, and the
  signature of a deterministic split. **This surfaced as a suite failure, not as
  a hunch:** the A12 fixture builds blocks by exact division, which gave
  σ̂ = 0.002 and **90 manufactured flags** on data whose binomial pulls never
  exceed 0.06. The raw σ̂ is still reported; only the statistic is floored.
- **A calibration check.** On synthetic genuinely-binomial data σ̂ recovers
  **~1.0** (1.017 ± 0.077 over 20 seeds). That is what licenses reading σ̂ = 4.4
  as "4.4× overdispersed" rather than as an unscaled number.

The pinned test grew **three checks → eight**. The new ones cover the MAD null's
negative control, its injected positive **at its own scale** (a 10-binomial-σ bin
is a 2.3 σ event under a 4.4-wide null, so testing at the binomial scale would
test the wrong instrument), its calibration, and the floor.

**Six documents annotated, none rewritten.** "30 of 88" stands everywhere as the
historical computation, with the recalibrated count dated beside it. R10 gained
`--null binomial`; **R10b** pins the mad result. README and the plan's recipe
list were updated so every committed invocation still runs.

---

## 2. MONASH RE-EXTRACTED — E5 confirmed

The corrected table stops being an arithmetic inversion. The fixed extractor ran
against the merged pair files, central and all ten blocks, ROOT 6.30/01 **on
pin**.

| quantity | predicted (reconstruction) | **measured** |
|---|---|---|
| total | 53,662,414 … 53,662,828 | **53,662,416** — 2 counts above the floor |
| kCentralGround | 52.4958 | **52.4959 ± 0.0074** |
| kExcludedVector | 46.4946 | **46.4946 ± 0.0079** |
| kExcludedExcited | 1.0095 | **1.0095 ± 0.0012** |
| charm : beauty | 89.9852 : 10.0148 | **89.9852 : 10.0148** — exact |
| D⁰ (v2 split) | 25.4542 | **25.4543 ± 0.0038** |
| B⁺ (v2 split) | 2.1440 | **2.1441 ± 0.0017** |

The 414-count bracket was the irreducible ambiguity of the eight mixed
beauty-charm species. **The reconstruction and the fix confirm each other.**

**The replication is now measured, not inferred.** E5 was diagnosed from
divisibility arithmetic on a committed CSV; the extractor reads the pairing from
the signed registry and reports `charm [24]x, beauty [26]x` in all eleven
directories.

**Per-event plausibility — the standing check:** **0.5366** per event against the
replicated **12.9866**. The published number was ~13 closure entries per event
and nobody divided.

**Integrity:** I3 exact, 53,662,416 both sides bin by bin. **I2 clean — 0 flags
in 10 comparisons**, where the retired binomial null gave 353 in 880. The
recalibration paying off on real data, the same day it landed.

**Block SEMs recomputed on the deduplicated blocks**, superseding the
replicated-era column. **They barely moved** — 0.0074 / 0.0079 / 0.0012,
unchanged to four places. That is expected rather than reassuring: a fraction's
block-to-block scatter is largely insensitive to a within-sector replication.
The old column was right by construction, not by validation.

Committed as `AnalysisScripts/anchors/merged_monash_dedup/` with a manifest and a
regenerate recipe that runs.

> **Deployment note that matters for the next session.** The fixed extractor was
> staged at `/data/alice/ipardoza/extractor_e5fix/`, **outside** the frozen
> checkout, because the merge reads that checkout live until its 33rd promotion
> (v41 §5). **`/data/alice/ipardoza/extract_species_decomposition.py` — the one
> the chains call — is still the OLD replicating version.** Relaunching a chain
> without redirecting it would silently reproduce E5.

---

## 3. THE 0.0018 % CLAIM — implemented, not withdrawn

The brief offered two outcomes: implement the derivation, or withdraw the claim.
**It turned out to be derivable, so it was implemented.**

`second_branch_weight.py` gains `--v2-map` (recipe **R8b**): a species' exposed
fraction is `1 − max(species-level branch fraction)`, summed over species that
were **not** split by map v2.

**It was confirmed, not fitted.** One definition reproduces **three** published
quantities at once, none of them targeted: pre-split **5.7737 %**, post-split
**0.0018 %**, and the per-species breakdown **B_c⁺ 0.000903 / B_c⁻ 0.000896**
("B_c± alone, 0.0009 % each"). A single agreement could be rounding luck; three
simultaneous ones, including a split never quoted as a target, are a derivation.
**The rounded value was never used as an input.**

**And the number moves under E5.** The residual is carried entirely by **B_c±, a
mixed beauty-charm species** — exactly the cross-sector quantity the replication
biased. On the re-extracted weights it is **0.0017 %** (B_c⁻ 0.000838, B_c⁺
0.000819). C6 passes by ~590.

---

## 4. WHAT THIS SESSION DID NOT DELIVER

Stated plainly, because the brief's central deliverable is among them.

- **The three-tune central table does not exist and could not.** JUNCTIONS has
  central + blocks 1–3; CLOSEPACKING has nothing. **No closure verdict is
  possible for either** — closure compares a central against its ten blocks.
- **The per-tune b-baryon asymmetry advisory table** needs the same three tunes.
  Not produced.
- **JUNCTIONS central was extracted opportunistically** (it is merged and
  promoted) as a head start for the next session — see the appendix. It is
  **NOT closure-verified and has no SEMs**, and must not be quoted as a result.
- **The merge's 65–77 h band cannot be scored**: the run never finished. It was
  killed at 15/33 after ~48.6 h. Scoring a band against an interrupted run would
  be scoring nothing.
- **Not touched, by instruction:** the pair-level unresolved systematic,
  plotting, Nikhef disk consolidation, `Paper/**`.
- **The environment was off-pin for all local work** (ROOT 6.38 against a pinned
  6.30/01, no PYTHIA); every local run here is pure Python under
  `HF_ALLOW_UNPINNED_ENV=1`. **The Nikhef extraction was on pin.**

---

## 5. FOR THE NEXT SESSION

1. **Check the merge first** — `merge_v4.log`, count `PROMOTED_MERGE`, and use
   `rchar` rather than atime to judge liveness. Expect another maintenance
   reboot eventually; the driver resumes, so just relaunch it.
2. **The chains are dead and their extractor is the old one.** Point any
   relaunch at `extractor_e5fix/`, or re-extract afterwards as was done here.
3. **Harvest JUNCTIONS then CLOSEPACKING** when their ten blocks land: closure
   verdict against the 2100/1500 pre-registration with the required schema
   argument, then `decompose_with_block_sems.py` (I2 now MAD, I3 unchanged).
4. **Then the three-tune table**, marked FINAL only if closure passed and
   integrity is clean for all three.
5. **The 1.6 G orphaned stage** is still there and can be removed once the
   JUNCTIONS block 4 promotion lands.

---

## APPENDIX — JUNCTIONS central, PROVISIONAL, NOT A RESULT

> ## ⛔ DO NOT QUOTE THIS
>
> **No closure verdict exists for JUNCTIONS** and cannot until its ten blocks
> are merged — closure is precisely a central-against-its-ten-blocks identity.
> **There are no SEMs**, because a SEM needs the ten blocks too. This is one
> number per bin from one directory. It is recorded so the next session starts
> with a sanity read, not so anything can be built on it.

Extracted with the same fixed extractor, same pins, from the promoted
`complete_root_HF_RUN3_V1_JUNCTIONS`. Self-check **AGREE**, invariance
**CONSERVED**, replication measured as **charm [24]x, beauty [26]x**.

| | MONASH (certified) | JUNCTIONS (provisional) |
|---|---|---|
| total | 53,662,416 | 46,311,148 |
| per event | 0.5366 | **0.4631** — plausible |
| filled species ordinals | 95 | **135** |
| kCentralGround % | 52.4959 | **58.2318** |
| kExcludedVector % | 46.4946 | **39.9409** |
| kExcludedExcited % | 1.0095 | **1.7821** |
| kMultiplyHeavy % | 0.0000 (8 entries) | **0.0452** (20,935 entries) |

**The direction is the one a junction tune predicts** — more central-ground
weight, more excited states, three orders more doubly-heavy — and forty more
species are populated at all. **That is a reason to finish the harvest, not a
finding.** The tune-bundle confound stands: JUNCTIONS re-tunes `StringFlav` and
`StringZ` alongside `ColourReconnection` (28 allowed differences across nine
families, only 8 of them CR), so a MONASH-vs-JUNCTIONS difference in a baryon
observable **cannot** be attributed to junction formation alone.
